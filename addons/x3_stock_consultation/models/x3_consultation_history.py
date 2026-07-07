from odoo import models, fields


class ConsultationHistory(models.Model):
    """
    Historique des consultations par les utilisateurs.
    Permet le suivi d'accès et l'audit (obligatoire pour 30 jours de rétention).
    """
    _name = 'x3.consultation.history'
    _description = 'Historique des consultations'
    _order = 'consultation_date DESC'
    _rec_name = 'consultation_date'

    consultation_date = fields.Datetime(
        string='Date consultation',
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    user_id = fields.Many2one(
        string='Utilisateur',
        comodel_name='res.users',
        required=True,
        default=lambda self: self.env.user,
        index=True,
    )
    article_code = fields.Char(
        string='Code article consulté',
        index=True,
    )
    article_name = fields.Char(
        string='Désignation',
    )
    consultation_type = fields.Selection(
        string='Type de consultation',
        selection=[
            ('list', 'Liste'),
            ('form', 'Fiche détail'),
            ('search', 'Recherche'),
            ('export', 'Export'),
        ],
        default='list',
        required=True,
    )
