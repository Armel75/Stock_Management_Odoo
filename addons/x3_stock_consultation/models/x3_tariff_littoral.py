from odoo import models, fields


class TariffLittoral(models.Model):
    """
    Tarifaire du Littoral (vue SQL Server ZPRIXLTT).
    Prix, quantités par article pour la région LTT.
    """
    _name = 'x3.tariff.littoral'
    _description = 'Tarifaire du Littoral'
    _order = 'default_code ASC, min_qty ASC'
    _rec_name = 'default_code'

    default_code = fields.Char(
        string='CODE X3',
        index=True,
        required=True,
        help='PLICRI2_0 depuis ZPRIXLTT',
    )
    name = fields.Char(
        string='DÉSIGNATION',
        help='ITMDES1_0 depuis ZPRIXLTT',
    )
    plicri3 = fields.Char(
        string='FAMILLE STAT',
        help='PLICRI3_0 depuis ZPRIXLTT',
    )
    price_ht = fields.Float(
        string='PRIX HT',
        digits=(16, 6),
        help='PRIXHT_0 depuis ZPRIXLTT',
    )
    price_ttc = fields.Float(
        string='PRIX TTC',
        digits=(16, 6),
        help='PRIXTTC_0 depuis ZPRIXLTT',
    )
    min_qty = fields.Float(
        string='QTE MIN',
        help='MINQTY_0 depuis ZPRIXLTT',
    )
    max_qty = fields.Float(
        string='QTE MAX',
        help='MAXQTY_0 depuis ZPRIXLTT',
    )
    text = fields.Text(
        string='Texte',
        help='TEXTE_0 depuis ZPRIXLTT',
    )
