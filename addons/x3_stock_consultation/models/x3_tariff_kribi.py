from odoo import models, fields


class TariffKribi(models.Model):
    """
    Tarifaire de Kribi (vue SQL Server ZPRIXKRI).
    Prix, quantités par article pour la région KRI.
    """
    _name = 'x3.tariff.kribi'
    _description = 'Tarifaire de Kribi'
    _order = 'default_code ASC, min_qty ASC'
    _rec_name = 'default_code'

    default_code = fields.Char(
        string='CODE X3',
        index=True,
        required=True,
        help='PLICRI2_0 depuis ZPRIXKRI',
    )
    name = fields.Char(
        string='DÉSIGNATION',
        help='ITMDES1_0 depuis ZPRIXKRI',
    )
    plicri3 = fields.Char(
        string='FAMILLE STAT',
        help='PLICRI3_0 depuis ZPRIXKRI',
    )
    price_ht = fields.Float(
        string='PRIX HT',
        digits=(16, 6),
        help='PRIXHT_0 depuis ZPRIXKRI',
    )
    price_ttc = fields.Float(
        string='PRIX TTC',
        digits=(16, 6),
        help='PRIXTTC_0 depuis ZPRIXKRI',
    )
    min_qty = fields.Float(
        string='QTE MIN',
        help='MINQTY_0 depuis ZPRIXKRI',
    )
    max_qty = fields.Float(
        string='QTE MAX',
        help='MAXQTY_0 depuis ZPRIXKRI',
    )
    text = fields.Text(
        string='Texte',
        help='TEXTE_0 depuis ZPRIXKRI',
    )
