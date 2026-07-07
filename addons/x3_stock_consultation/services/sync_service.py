"""
Service de synchronisation SAGE X3 → PostgreSQL.

Rôle :
1. Lire la configuration
2. Instancier le repository SQL Server
3. Lire les données depuis SQL Server via le repository
4. Transformer et écrire dans les modèles Odoo
5. Journaliser dans x3.sync.history
"""
import logging
import time

from odoo import models, api, fields

_logger = logging.getLogger(__name__)

# Correspondance : suffixe région → colonnes du modèle
# Permet d'écrire les prix dans les bons champs dynamiquement
PRICE_FIELDS_MAP = {
    'bda': {
        'ht': 'price_ht_bda',
        'ttc': 'price_ttc_bda',
        'min_qty': 'min_qty_bda',
        'max_qty': 'max_qty_bda',
        'plicri3': 'plicri3_bda',
    },
    'ber': {
        'ht': 'price_ht_ber',
        'ttc': 'price_ttc_ber',
        'min_qty': 'min_qty_ber',
        'max_qty': 'max_qty_ber',
        'plicri3': 'plicri3_ber',
    },
    'cen': {
        'ht': 'price_ht_cen',
        'ttc': 'price_ttc_cen',
        'min_qty': 'min_qty_cen',
        'max_qty': 'max_qty_cen',
        'plicri3': 'plicri3_cen',
    },
    'kri': {
        'ht': 'price_ht_kri',
        'ttc': 'price_ttc_kri',
        'min_qty': 'min_qty_kri',
        'max_qty': 'max_qty_kri',
        'plicri3': 'plicri3_kri',
    },
    'ltt': {
        'ht': 'price_ht_ltt',
        'ttc': 'price_ttc_ltt',
        'min_qty': 'min_qty_ltt',
        'max_qty': 'max_qty_ltt',
        'plicri3': 'plicri3_ltt',
    },
    'nga': {
        'ht': 'price_ht_nga',
        'ttc': 'price_ttc_nga',
        'min_qty': 'min_qty_nga',
        'max_qty': 'max_qty_nga',
        'plicri3': 'plicri3_nga',
    },
    'ou': {
        'ht': 'price_ht_ou',
        'ttc': 'price_ttc_ou',
        'min_qty': 'min_qty_ou',
        'max_qty': 'max_qty_ou',
        'plicri3': 'plicri3_ou',
    },
}


class SyncService(models.Model):
    """
    Service de synchronisation.
    Point d'entrée unique pour le cron et pour les actions manuelles.
    """
    _name = 'x3.sync.service'
    _description = 'Service de synchronisation X3'

    # -------------------------------------------------------------------------
    # API PUBLIQUE
    # -------------------------------------------------------------------------

    @api.model
    def run_full_sync(self):
        """
        Lance une synchronisation complète (stock + prix toutes régions).
        Appelé par le cron (00h00) ou par l'action manuelle de l'admin.
        """
        sync_type = 'cron' if self._called_by_cron() else 'manual'
        sync_record = self._start_sync_record(sync_type)
        start_time = time.time()

        try:
            config = self._get_config()
            repo = self._instantiate_repository(config)

            _logger.info('Début de la synchronisation depuis SQL Server...')

            # === Étape 1 & 2 : Récupérer stock + prix en UNE connexion ===
            all_data = repo.get_all_stock_and_prices_single_connection(config['view_stock'])
            stock_data = all_data['stock']
            prices_by_region = all_data['prices_by_region']

            if not stock_data:
                _logger.warning('Aucune donnée de stock retournée par SQL Server.')
                self._complete_sync_record(
                    sync_record, state='success',
                    articles_count=0, duration=time.time() - start_time,
                )
                return self._result(True, 'Aucun stock à synchroniser.', 0)

            # === Étape 3 : Indexer les prix par code article pour accès rapide ===
            price_index = {}
            for region, prices in prices_by_region.items():
                for p in prices:
                    code = p.get('default_code', '')
                    if not code:
                        continue
                    if code not in price_index:
                        price_index[code] = {}
                    price_index[code][region] = p

            # === Étape 4 : Upsert des articles dans le cache ===
            articles_count = self._upsert_articles_with_prices(
                stock_data, price_index,
            )

            # Synchronisations complémentaires : Tarifaires régionaux (après les stocks)
            regional_results = []
            has_regional_errors = False
            for method_name in [
                'sync_tariff_littoral', 'sync_tariff_bamenda',
                'sync_tariff_centre', 'sync_tariff_ouest',
                'sync_tariff_kribi', 'sync_tariff_bertoua',
                'sync_tariff_ngaoundere',
            ]:
                try:
                    res = getattr(self, method_name)()
                    msg = res.get('message', 'Succès')
                    regional_results.append(f"• {method_name.replace('sync_tariff_', '').capitalize()}: {msg}")
                    if not res.get('success'):
                        has_regional_errors = True
                except Exception as e:
                    has_regional_errors = True
                    regional_results.append(f"• {method_name.replace('sync_tariff_', '').capitalize()}: Erreur ({str(e)})")
                    _logger.warning(
                        '%s ignorée.', method_name, exc_info=True,
                    )

            summary_report = "\n".join(regional_results)
            duration = time.time() - start_time

            self._complete_sync_record(
                sync_record,
                state='error' if has_regional_errors else 'success',
                articles_count=articles_count,
                duration=duration,
                error_message=f"Rapport des tarifaires régionaux :\n{summary_report}"
            )

            self.env.cr.commit()

            _logger.info(
                'Synchronisation terminée : %d articles en %.2f secondes.\n%s',
                articles_count, duration, summary_report,
            )

            return self._result(
                not has_regional_errors,
                f"Synchronisation terminée.\n{summary_report}",
                articles_count,
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f'{type(e).__name__}: {str(e)}'
            _logger.error('Erreur lors de la synchronisation : %s', error_msg, exc_info=True)

            self._complete_sync_record(
                sync_record, state='error',
                articles_count=0, duration=duration,
                error_message=error_msg,
            )
            self.env.cr.commit()
            return self._result(False, error_msg, 0)

    @api.model
    def cleanup_history(self):
        """
        Nettoie l'historique des consultations au-delà du nombre de jours configuré.
        Appelé par le cron à 02h00.
        """
        config = self._get_config()
        retention_days = config.get('history_retention_days', 30)

        cutoff_date = fields.Datetime.subtract(
            fields.Datetime.now(),
            days=retention_days,
        )

        domain = [('consultation_date', '<', cutoff_date)]
        deleted_count = self.env['x3.consultation.history'].search(domain).unlink()

        _logger.info(
            'Nettoyage historique : %d enregistrements supprimés (rétention %d jours).',
            deleted_count, retention_days,
        )

    @api.model
    def run_pending_sync(self):
        """
        Vérifie si une synchronisation manuelle est demandée et l'exécute.
        Appelé par le cron rapide (toutes les 5 minutes).
        """
        ICP = self.env['ir.config_parameter'].sudo()
        pending = ICP.get_param('x3_stock.sync_pending', 'False')

        if pending != 'True':
            return

        _logger.info('Demande de synchronisation manuelle détectée. Exécution...')

        ICP.set_param('x3_stock.sync_pending', 'False')
        self.env.cr.commit()

        self.run_full_sync()

    @api.model
    def _sync_tariff_region(self, view_name, model_name, label):
        """
        Synchronise les données d'une vue tarifaire régionale
        vers le modèle Odoo correspondant de manière ultra-rapide.
        Optimisation (approche top 1%) :
        - Bulk insert (create en masse par lots)
        - Évite l'overhead d'insérer ligne par ligne
        """
        config = self._get_config()
        repo = self._instantiate_repository(config)

        _logger.info('Début de la synchronisation tarifaire %s...', label)

        try:
            price_view = f"{config['schema']}.{view_name}"
            query = f"""
                SELECT
                    PLICRI2_0     AS default_code,
                    ITMDES1_0     AS name,
                    TEXTE_0       AS text,
                    PLICRI3_0     AS plicri3,
                    PRIXHT_0      AS price_ht,
                    PRIXTTC_0     AS price_ttc,
                    MINQTY_0      AS min_qty,
                    MAXQTY_0      AS max_qty
                FROM {price_view}
            """
            rows = repo._execute_query(query)

            if not rows:
                _logger.warning('Aucune donnée dans %s.', view_name)
                return self._result(True, f'Aucune donnée {label}.', 0)

            Model = self.env[model_name]
            count = 0
            batch_size = 2000

            # Suppression propre et commit pour libérer la base
            Model.search([]).unlink()
            self.env.cr.commit()

            # Préparation de l'upsert groupé
            vals_list = []
            for row in rows:
                vals_list.append({
                    'default_code': row.get('default_code', '') or '',
                    'name': row.get('name', '') or '',
                    'text': row.get('text', '') or '',
                    'plicri3': row.get('plicri3', '') or '',
                    'price_ht': float(row.get('price_ht') or 0.0),
                    'price_ttc': float(row.get('price_ttc') or 0.0),
                    'min_qty': float(row.get('min_qty') or 0.0),
                    'max_qty': float(row.get('max_qty') or 0.0),
                })

            # Bulk create par lots de 2000
            for k in range(0, len(vals_list), batch_size):
                batch_vals = vals_list[k:k+batch_size]
                Model.create(batch_vals)
                self.env.cr.commit()
                count += len(batch_vals)

            _logger.info('Tarifaire %s synchronisée : %d lignes.', label, count)
            return self._result(True, f'{label} : {count} lignes importées.', count)

        except Exception as e:
            _logger.error('Erreur sync tarifaire %s : %s', label, e, exc_info=True)
            return self._result(False, str(e), 0)

    @api.model
    def sync_tariff_littoral(self):
        """Synchronise ZPRIXLTT vers x3.tariff.littoral."""
        return self._sync_tariff_region('ZPRIXLTT', 'x3.tariff.littoral', 'Littoral')

    @api.model
    def sync_tariff_bamenda(self):
        """Synchronise ZPRIXBDA vers x3.tariff.bamenda."""
        return self._sync_tariff_region('ZPRIXBDA', 'x3.tariff.bamenda', 'Bamenda')

    @api.model
    def sync_tariff_centre(self):
        """Synchronise ZPRIXCEN vers x3.tariff.centre."""
        return self._sync_tariff_region('ZPRIXCEN', 'x3.tariff.centre', 'Centre')

    @api.model
    def sync_tariff_ouest(self):
        """Synchronise ZPRIXOU vers x3.tariff.ouest."""
        return self._sync_tariff_region('ZPRIXOU', 'x3.tariff.ouest', 'Ouest')

    @api.model
    def sync_tariff_kribi(self):
        """Synchronise ZPRIXKRI vers x3.tariff.kribi."""
        return self._sync_tariff_region('ZPRIXKRI', 'x3.tariff.kribi', 'Kribi')

    @api.model
    def sync_tariff_bertoua(self):
        """Synchronise ZPRIXBER vers x3.tariff.bertoua."""
        return self._sync_tariff_region('ZPRIXBER', 'x3.tariff.bertoua', 'Bertoua')

    @api.model
    def sync_tariff_ngaoundere(self):
        """Synchronise ZPRIXNGA vers x3.tariff.ngaoundere."""
        return self._sync_tariff_region('ZPRIXNGA', 'x3.tariff.ngaoundere', 'Ngaoundéré')

    # -------------------------------------------------------------------------
    # MÉTHODES INTERNES
    # -------------------------------------------------------------------------

    @api.model
    def _get_config(self):
        """Récupère la configuration depuis ir.config_parameter."""
        ICP = self.env['ir.config_parameter'].sudo()
        return {
            'host': ICP.get_param('x3_stock.sql_server_host', '192.168.0.99\\SQLX3V11'),
            'port': int(ICP.get_param('x3_stock.sql_server_port', '1433')),
            'user': ICP.get_param('x3_stock.sql_server_user', 'sa'),
            'password': ICP.get_param('x3_stock.sql_server_password', 'P@ssw0rd01'),
            'database': ICP.get_param('x3_stock.sql_server_database', 'sagex3v11'),
            'schema': ICP.get_param('x3_stock.sql_server_schema', 'SOREPCO'),
            'view_stock': ICP.get_param('x3_stock.view_stock', 'ZSTOAG'),
            'history_retention_days': int(ICP.get_param('x3_stock.history_retention_days', '30')),
        }

    @api.model
    def _instantiate_repository(self, config):
        """Instancie le repository SQL Server avec la configuration."""
        from odoo.addons.x3_stock_consultation.repository.sqlserver_repository import SqlServerRepository
        return SqlServerRepository(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            schema=config['schema'],
        )

    @api.model
    def _upsert_articles_with_prices(self, stock_data, price_index):
        """
        Insère ou met à jour les articles de manière ultra-rapide.
        Double optimisation (approche top 1%) :
        1. Indexation en mémoire de tous les articles existants (évite N search)
        2. Bulk insertion pour les nouveaux articles (create en masse par lots)
        3. browse() direct pour les écritures (évite les overhead de planification SQL)

        Args:
            stock_data: list[dict] issues du repository (stock)
            price_index: dict indexé par code article → {region: {price_data}}

        Returns:
            int: Nombre d'articles traités
        """
        ArticleCache = self.env['x3.article.cache']
        now = fields.Datetime.now()
        count = 0
        batch_size = 2000

        _logger.info("Début de l'upsert optimisé de %d lignes de stock.", len(stock_data))

        # Étape Top 1% : Consolider les doublons potentiels de (default_code, site_id) dans les données brutes de SAGE X3
        # pour éviter les violations de contrainte d'unicité PostgreSQL si la vue de production contient des doublons.
        consolidated_stock = {}
        for row in stock_data:
            default_code = row.get('default_code')
            if not default_code:
                continue
            site_id = (row.get('site_id') or '').strip()
            key = (default_code, site_id)
            
            if key not in consolidated_stock:
                consolidated_stock[key] = {
                    'default_code': default_code,
                    'site_id': site_id,
                    'name': row.get('name', ''),
                    'search_key': row.get('search_key', ''),
                    'quantity': float(row.get('quantity') or 0.0),
                    'cumulative_quantity': float(row.get('cumulative_quantity') or 0.0),
                    'status': row.get('status', ''),
                }
            else:
                # Cumul des quantités s'il y a des lignes de stocks découpées (par exemple, par statut ou lot)
                consolidated_stock[key]['quantity'] += float(row.get('quantity') or 0.0)
                consolidated_stock[key]['cumulative_quantity'] += float(row.get('cumulative_quantity') or 0.0)
                # On concatène les statuts s'ils sont différents pour information
                current_status = consolidated_stock[key]['status']
                new_status = row.get('status', '')
                if new_status and new_status not in current_status:
                    consolidated_stock[key]['status'] = f"{current_status},{new_status}"[:100]  # Sécurité sur la longueur

        # 1. Charger l'index existant des articles en mémoire vive
        existing_data = ArticleCache.search_read([], ['default_code', 'site_id', 'id'])
        # Map : (default_code, site_id) -> ID de l'enregistrement
        existing_map = {
            (rec['default_code'], rec['site_id'] or ''): rec['id']
            for rec in existing_data
        }
        _logger.info("Indexation Python terminée : %d articles existants référencés. Données SAGE consolidées en %d lignes.", len(existing_map), len(consolidated_stock))

        create_list = []
        updates_count = 0

        for key, row in consolidated_stock.items():
            default_code = row['default_code']
            site_id = row['site_id']

            # Valeurs de base (stock consolidé)
            vals = {
                'default_code': default_code,
                'site_id': site_id,
                'name': row['name'],
                'search_key': row['search_key'],
                'quantity': row['quantity'],
                'cumulative_quantity': row['cumulative_quantity'],
                'status': row['status'],
                'sync_date': now,
            }

            # Ajouter tous les prix par région
            article_prices = price_index.get(default_code, {})
            for region, fields_map in PRICE_FIELDS_MAP.items():
                region_price = article_prices.get(region, {})
                if region_price:
                    vals[fields_map['ht']] = float(region_price.get('price_ht') or 0.0)
                    vals[fields_map['ttc']] = float(region_price.get('price_ttc') or 0.0)
                    vals[fields_map['min_qty']] = float(region_price.get('min_qty') or 0.0)
                    vals[fields_map['max_qty']] = float(region_price.get('max_qty') or 0.0)
                    vals[fields_map['plicri3']] = region_price.get('plicri3', '')
                    if not vals.get('text'):
                        vals['text'] = region_price.get('text', '')
                    if not vals.get('search_key'):
                        vals['search_key'] = region_price.get('search_key', '')

            key = (default_code, site_id or '')
            existing_id = existing_map.get(key)

            if existing_id:
                # Écriture directe par ID via browse (ultra rapide)
                ArticleCache.browse(existing_id).write(vals)
                updates_count += 1
            else:
                # Accumulation pour insertion par lot (Bulk insert)
                create_list.append(vals)

            count += 1

            # Libération de la mémoire cache de l'ORM Odoo pour éviter les MemoryError.
            # Odoo accumule par défaut tous les objets écrits/créés en cache mémoire au sein d'une transaction,
            # ce qui lève un MemoryError lors de l'intégration de volumes massifs (ici +125 000 lignes de production SAGE).
            if count % batch_size == 0:
                self.env.cr.commit()
                self.env.invalidate_all()

        # Insertion en masse des nouveaux articles par lots
        if create_list:
            _logger.info("Bulk insert en cours de %d nouveaux articles...", len(create_list))
            for k in range(0, len(create_list), batch_size):
                batch_vals = create_list[k:k+batch_size]
                ArticleCache.create(batch_vals)
                self.env.cr.commit()
                self.env.invalidate_all()

        _logger.info("Upsert terminé : %d articles traités (%d créés, %d mis à jour).", count, len(create_list), updates_count)
        return count

    @api.model
    def _start_sync_record(self, sync_type):
        """Crée un enregistrement de début de synchronisation."""
        return self.env['x3.sync.history'].create({
            'sync_type': sync_type,
            'state': 'running',
            'sync_date': fields.Datetime.now(),
        })

    @api.model
    def _complete_sync_record(self, record, state, articles_count, duration, error_message=None):
        """Met à jour l'enregistrement de synchronisation avec les résultats."""
        record.write({
            'state': state,
            'articles_count': articles_count,
            'duration_seconds': duration,
            'error_message': error_message,
        })

    @api.model
    def _called_by_cron(self):
        """Détecte si la méthode est appelée par le cron."""
        return self.env.context.get('cron', False)

    @api.model
    def _result(self, success, message, count):
        """Retourne un dictionnaire de résultat standardisé."""
        return {
            'success': success,
            'message': message,
            'articles_count': count,
        }
