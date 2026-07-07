from odoo import models, fields


class SyncHistory(models.Model):
    """
    Historique de chaque synchronisation : suivi, monitoring, débogage.
    Permet à l'administrateur de voir si la synchro de la nuit s'est bien passée.
    """
    _name = 'x3.sync.history'
    _description = 'Historique des synchronisations X3'
    _order = 'sync_date DESC'
    _rec_name = 'sync_date'

    sync_date = fields.Datetime(
        string='Date et heure',
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    sync_type = fields.Selection(
        string='Type',
        selection=[
            ('manual', 'Manuelle'),
            ('cron', 'Automatique (cron)'),
        ],
        default='cron',
        required=True,
    )
    state = fields.Selection(
        string='Statut',
        selection=[
            ('running', 'En cours'),
            ('success', 'Succès'),
            ('error', 'Erreur'),
        ],
        default='running',
        required=True,
        index=True,
    )
    articles_count = fields.Integer(
        string='Articles synchronisés',
        help='Nombre total d\'articles mis à jour durant cette synchro',
        default=0,
    )
    duration_seconds = fields.Float(
        string='Durée (secondes)',
        help='Durée totale de la synchronisation en secondes',
        default=0.0,
    )
    error_message = fields.Text(
        string='Message d\'erreur',
        help='Détail de l\'erreur en cas d\'échec',
    )
    version = fields.Char(
        string='Version du module',
        help='Version du module au moment de la synchro',
        default='1.0.0',
    )
