from odoo import models, fields, api


class SyncConfiguration(models.Model):
    """
    Configuration de la connexion SQL Server et des paramètres de synchronisation.
    L'administrateur peut modifier ces valeurs depuis l'interface Odoo.
    
    Les valeurs sont stockées dans ir.config_parameter pour la persistance,
    mais ce modèle offre une interface utilisateur propre pour les modifier.
    """
    _name = 'x3.sync.configuration'
    _description = 'Configuration synchronisation X3'
    _rec_name = 'display_name'

    display_name = fields.Char(
        string='Configuration',
        compute='_compute_display_name',
        store=False,
    )

    # === Connexion SQL Server ===
    sql_server_host = fields.Char(
        string='Hôte SQL Server',
        help='Adresse IP ou nom d\'hôte du serveur SQL Server (ex: 192.168.0.99\\SQLX3V11)',
        default=lambda self: self._get_param('x3_stock.sql_server_host', '192.168.0.99\\SQLX3V11'),
    )
    sql_server_port = fields.Integer(
        string='Port SQL Server',
        default=lambda self: int(self._get_param('x3_stock.sql_server_port', '1433')),
    )
    sql_server_user = fields.Char(
        string='Utilisateur SQL Server',
        default=lambda self: self._get_param('x3_stock.sql_server_user', 'sa'),
    )
    sql_server_password = fields.Char(
        string='Mot de passe SQL Server',
        default=lambda self: self._get_param('x3_stock.sql_server_password', 'P@ssw0rd01'),
    )
    sql_server_database = fields.Char(
        string='Base de données SQL Server',
        default=lambda self: self._get_param('x3_stock.sql_server_database', 'sagex3v11'),
    )
    sql_server_schema = fields.Char(
        string='Schéma SQL Server',
        default=lambda self: self._get_param('x3_stock.sql_server_schema', 'SOREPCO'),
        help='Schéma SQL Server contenant les vues (ex: SOREPCO, dbo)',
    )

    # === Paramètres de synchronisation ===
    sync_interval_hours = fields.Integer(
        string='Intervalle synchro (heures)',
        default=lambda self: int(self._get_param('x3_stock.sync_interval_hours', '24')),
        help='Fréquence de synchronisation automatique en heures',
    )
    history_retention_days = fields.Integer(
        string='Rétention historique (jours)',
        default=lambda self: int(self._get_param('x3_stock.history_retention_days', '30')),
        help='Nombre de jours de conservation de l\'historique des consultations',
    )

    # === Vue SQL Server (noms) ===
    view_stock_name = fields.Char(
        string='Vue stocks',
        default=lambda self: self._get_param('x3_stock.view_stock', 'ZSTOAG'),
        help='Nom de la vue SQL Server pour les stocks',
    )
    view_price_name = fields.Char(
        string='Vue prix',
        default='ZPRIXBDA',
        help='Nom de la vue SQL Server pour les prix',
    )

    # === Informations résumées ===
    last_sync_date = fields.Datetime(
        string='Dernière synchro',
        compute='_compute_last_sync',
        store=False,
    )
    last_sync_state = fields.Char(
        string='Dernier statut',
        compute='_compute_last_sync',
        store=False,
    )
    last_sync_duration = fields.Float(
        string='Dernière durée (s)',
        compute='_compute_last_sync',
        store=False,
    )

    def _get_param(self, key, default=''):
        return self.env['ir.config_parameter'].sudo().get_param(key, default)

    def _set_param(self, key, value):
        self.env['ir.config_parameter'].sudo().set_param(key, str(value))

    @api.depends('sql_server_host')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f'X3 - {record.sql_server_host or "Non configuré"}'

    @api.depends()
    def _compute_last_sync(self):
        for record in self:
            last_sync = self.env['x3.sync.history'].search(
                [],
                order='sync_date DESC',
                limit=1,
            )
            if last_sync:
                record.last_sync_date = last_sync.sync_date
                record.last_sync_state = dict(last_sync._fields['state'].selection).get(last_sync.state)
                record.last_sync_duration = last_sync.duration_seconds
            else:
                record.last_sync_date = False
                record.last_sync_state = 'Jamais'
                record.last_sync_duration = 0.0

    def action_save_configuration(self):
        """Sauvegarde la configuration dans ir.config_parameter"""
        self.ensure_one()
        self._set_param('x3_stock.sql_server_host', self.sql_server_host)
        self._set_param('x3_stock.sql_server_port', str(self.sql_server_port))
        self._set_param('x3_stock.sql_server_user', self.sql_server_user)
        self._set_param('x3_stock.sql_server_password', self.sql_server_password)
        self._set_param('x3_stock.sql_server_database', self.sql_server_database)
        self._set_param('x3_stock.sql_server_schema', self.sql_server_schema)
        self._set_param('x3_stock.sync_interval_hours', str(self.sync_interval_hours))
        self._set_param('x3_stock.history_retention_days', str(self.history_retention_days))
        self._set_param('x3_stock.view_stock', self.view_stock_name)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Configuration sauvegardée',
                'message': 'Les paramètres de synchronisation ont été mis à jour.',
                'type': 'success',
                'sticky': False,
            },
        }

    def action_test_connection(self):
        """Teste la connexion au serveur SQL Server"""
        self.ensure_one()
        from odoo.addons.x3_stock_consultation.repository.sqlserver_repository import SqlServerRepository
        repo = SqlServerRepository(
            host=self.sql_server_host,
            port=self.sql_server_port,
            user=self.sql_server_user,
            password=self.sql_server_password,
            database=self.sql_server_database,
            schema=self.sql_server_schema,
        )
        success, message = repo.test_connection()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Test de connexion',
                'message': message,
                'type': 'success' if success else 'danger',
                'sticky': not success,
            },
        }
