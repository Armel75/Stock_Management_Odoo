from odoo import models, fields


class TariffOuest(models.Model):
    """
    Tarifaire de l'Ouest (vue SQL Server ZPRIXOU).
    Prix, quantités par article pour la région OU.
    """
    _name = 'x3.tariff.ouest'
    _description = 'Tarifaire de l\'Ouest'
    _order = 'default_code ASC, min_qty ASC'
    _rec_name = 'default_code'

    default_code = fields.Char(
        string='CODE X3',
        index=True,
        required=True,
        help='PLICRI2_0 depuis ZPRIXOU',
    )
    name = fields.Char(
        string='DÉSIGNATION',
        help='ITMDES1_0 depuis ZPRIXOU',
    )
    plicri3 = fields.Char(
        string='FAMILLE STAT',
        help='PLICRI3_0 depuis ZPRIXOU',
    )
    price_ht = fields.Float(
        string='PRIX HT',
        digits=(16, 6),
        help='PRIXHT_0 depuis ZPRIXOU',
    )
    price_ttc = fields.Float(
        string='PRIX TTC',
        digits=(16, 6),
        help='PRIXTTC_0 depuis ZPRIXOU',
    )
    min_qty = fields.Float(
        string='QTE MIN',
        help='MINQTY_0 depuis ZPRIXOU',
    )
    max_qty = fields.Float(
        string='QTE MAX',
        help='MAXQTY_0 depuis ZPRIXOU',
    )
    text = fields.Text(
        string='Texte',
        help='TEXTE_0 depuis ZPRIXOU',
    )
