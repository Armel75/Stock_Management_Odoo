from odoo import models, fields


class TariffBertoua(models.Model):
    """
    Tarifaire de Bertoua (vue SQL Server ZPRIXBER).
    Prix, quantités par article pour la région BER.
    """
    _name = 'x3.tariff.bertoua'
    _description = 'Tarifaire de Bertoua'
    _order = 'default_code ASC, min_qty ASC'
    _rec_name = 'default_code'

    default_code = fields.Char(
        string='CODE X3',
        index=True,
        required=True,
        help='PLICRI2_0 depuis ZPRIXBER',
    )
    name = fields.Char(
        string='DÉSIGNATION',
        help='ITMDES1_0 depuis ZPRIXBER',
    )
    plicri3 = fields.Char(
        string='FAMILLE STAT',
        help='PLICRI3_0 depuis ZPRIXBER',
    )
    price_ht = fields.Float(
        string='PRIX HT',
        digits=(16, 6),
        help='PRIXHT_0 depuis ZPRIXBER',
    )
    price_ttc = fields.Float(
        string='PRIX TTC',
        digits=(16, 6),
        help='PRIXTTC_0 depuis ZPRIXBER',
    )
    min_qty = fields.Float(
        string='QTE MIN',
        help='MINQTY_0 depuis ZPRIXBER',
    )
    max_qty = fields.Float(
        string='QTE MAX',
        help='MAXQTY_0 depuis ZPRIXBER',
    )
    text = fields.Text(
        string='Texte',
        help='TEXTE_0 depuis ZPRIXBER',
    )
