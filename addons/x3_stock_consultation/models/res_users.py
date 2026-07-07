from odoo import models, fields, api


class ResUsers(models.Model):
    """
    Extension du modèle utilisateur Odoo.
    Ajoute le champ région de prix pour l'affichage des prix SAGE X3.
    """
    _inherit = 'res.users'

    x3_price_region = fields.Selection(
        string='Région de prix X3',
        selection=[
            ('bda', 'BDA'),
            ('ber', 'BER'),
            ('cen', 'CEN'),
            ('kri', 'KRI'),
            ('ltt', 'LTT'),
            ('nga', 'NGA'),
            ('ou', 'OU'),
        ],
        default='bda',
        required=True,
        help='Région de prix SAGE X3 associée à cet utilisateur.\n'
             'Les prix affichés dans la consultation correspondront à cette région.',
    )
