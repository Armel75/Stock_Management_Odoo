from odoo import models, fields, api


class ArticleCache(models.Model):
    """
    Cache PostgreSQL des articles, stocks et prix synchronisés depuis SAGE X3.
    Modèle central de consultation : toutes les lectures se font ici, jamais sur SQL Server.
    """
    _name = 'x3.article.cache'
    _description = 'Cache Article / Stock / Prix - SAGE X3'
    _order = 'default_code ASC'
    _rec_name = 'default_code'

    # === Article ===
    default_code = fields.Char(
        string='Code article',
        index=True,
        required=True,
        help='ITMREF_0 / PLICRI2_0 depuis les vues X3',
    )
    name = fields.Char(
        string='Désignation',
        help='ITMDES1_0 depuis les vues X3',
    )
    search_key = fields.Char(
        string='Clé de recherche',
        help='SEAKEY_0 depuis les vues X3',
        index=True,
    )
    text = fields.Text(
        string='Texte complémentaire',
        help='TEXTE_0 depuis la vue prix X3',
    )

    # === Stock ===
    site_id = fields.Char(
        string='Site / Dépôt',
        help='STOFCY_0 depuis la vue stock X3',
        index=True,
    )
    quantity = fields.Float(
        string='Quantité en stock',
        help='QTE_0 depuis la vue stock X3',
        group_operator='sum',
    )
    cumulative_quantity = fields.Float(
        string='Quantité cumulée',
        help='CUMALLQTY_0 depuis la vue stock X3',
        group_operator='sum',
    )
    status = fields.Char(
        string='Statut',
        help='STA_0 depuis la vue stock X3',
    )

    # === Prix par région (Approche A : un champ par région) ===
    # Région BDA
    price_ht_bda = fields.Float(string='Prix HT - BDA', digits=(16, 6),)
    price_ttc_bda = fields.Float(string='Prix TTC - BDA', digits=(16, 6),)
    min_qty_bda = fields.Float(string='Qté min - BDA',)
    max_qty_bda = fields.Float(string='Qté max - BDA',)
    plicri3_bda = fields.Char(string='PLICRI3 - BDA',)

    # Région BER
    price_ht_ber = fields.Float(string='Prix HT - BER', digits=(16, 6),)
    price_ttc_ber = fields.Float(string='Prix TTC - BER', digits=(16, 6),)
    min_qty_ber = fields.Float(string='Qté min - BER',)
    max_qty_ber = fields.Float(string='Qté max - BER',)
    plicri3_ber = fields.Char(string='PLICRI3 - BER',)

    # Région CEN
    price_ht_cen = fields.Float(string='Prix HT - CEN', digits=(16, 6),)
    price_ttc_cen = fields.Float(string='Prix TTC - CEN', digits=(16, 6),)
    min_qty_cen = fields.Float(string='Qté min - CEN',)
    max_qty_cen = fields.Float(string='Qté max - CEN',)
    plicri3_cen = fields.Char(string='PLICRI3 - CEN',)

    # Région KRI
    price_ht_kri = fields.Float(string='Prix HT - KRI', digits=(16, 6),)
    price_ttc_kri = fields.Float(string='Prix TTC - KRI', digits=(16, 6),)
    min_qty_kri = fields.Float(string='Qté min - KRI',)
    max_qty_kri = fields.Float(string='Qté max - KRI',)
    plicri3_kri = fields.Char(string='PLICRI3 - KRI',)

    # Région LTT
    price_ht_ltt = fields.Float(string='Prix HT - LTT', digits=(16, 6),)
    price_ttc_ltt = fields.Float(string='Prix TTC - LTT', digits=(16, 6),)
    min_qty_ltt = fields.Float(string='Qté min - LTT',)
    max_qty_ltt = fields.Float(string='Qté max - LTT',)
    plicri3_ltt = fields.Char(string='PLICRI3 - LTT',)

    # Région NGA
    price_ht_nga = fields.Float(string='Prix HT - NGA', digits=(16, 6),)
    price_ttc_nga = fields.Float(string='Prix TTC - NGA', digits=(16, 6),)
    min_qty_nga = fields.Float(string='Qté min - NGA',)
    max_qty_nga = fields.Float(string='Qté max - NGA',)
    plicri3_nga = fields.Char(string='PLICRI3 - NGA',)

    # Région OU
    price_ht_ou = fields.Float(string='Prix HT - OU', digits=(16, 6),)
    price_ttc_ou = fields.Float(string='Prix TTC - OU', digits=(16, 6),)
    min_qty_ou = fields.Float(string='Qté min - OU',)
    max_qty_ou = fields.Float(string='Qté max - OU',)
    plicri3_ou = fields.Char(string='PLICRI3 - OU',)

    # === Champ calculé : prix affiché selon la région de l'utilisateur ===
    displayed_price_ht = fields.Float(
        string='Prix HT',
        compute='_compute_displayed_prices',
        store=False,
        digits=(16, 6),
    )
    displayed_price_ttc = fields.Float(
        string='Prix TTC',
        compute='_compute_displayed_prices',
        store=False,
        digits=(16, 6),
    )

    @api.depends_context('x3_price_region')
    def _compute_displayed_prices(self):
        """Affiche le prix correspondant à la région de l'utilisateur connecté."""
        region = self.env.context.get('x3_price_region', 'bda')
        region_suffix = region.lower()

        ht_field = f'price_ht_{region_suffix}'
        ttc_field = f'price_ttc_{region_suffix}'

        for record in self:
            record.displayed_price_ht = getattr(record, ht_field, 0.0)
            record.displayed_price_ttc = getattr(record, ttc_field, 0.0)

    # === Métadonnées de synchronisation ===
    sync_date = fields.Datetime(
        string='Date synchro',
        help='Date et heure de la dernière synchronisation pour cet enregistrement',
        index=True,
    )

    _sql_constraints = [
        (
            'unique_article_site',
            'UNIQUE(default_code, site_id)',
            'Un même article dans le même site ne peut apparaître qu\'une seule fois.',
        ),
    ]
