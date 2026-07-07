from odoo import models, fields


class TariffBamenda(models.Model):
    """
    Tarifaire de Bamenda (vue SQL Server ZPRIXBDA).
    Prix, quantités par article pour la région BDA.
    """
    _name = 'x3.tariff.bamenda'
    _description = 'Tarifaire de Bamenda'
    _order = 'default_code ASC, min_qty ASC'
    _rec_name = 'default_code'

    default_code = fields.Char(
        string='CODE X3',
        index=True,
        required=True,
        help='PLICRI2_0 depuis ZPRIXBDA',
    )
    name = fields.Char(
        string='DÉSIGNATION',
        help='ITMDES1_0 depuis ZPRIXBDA',
    )
    plicri3 = fields.Char(
        string='FAMILLE STAT',
        help='PLICRI3_0 depuis ZPRIXBDA',
    )
    price_ht = fields.Float(
        string='PRIX HT',
        digits=(16, 6),
        help='PRIXHT_0 depuis ZPRIXBDA',
    )
    price_ttc = fields.Float(
        string='PRIX TTC',
        digits=(16, 6),
        help='PRIXTTC_0 depuis ZPRIXBDA',
    )
    min_qty = fields.Float(
        string='QTE MIN',
        help='MINQTY_0 depuis ZPRIXBDA',
    )
    max_qty = fields.Float(
        string='QTE MAX',
        help='MAXQTY_0 depuis ZPRIXBDA',
    )
    text = fields.Text(
        string='Texte',
        help='TEXTE_0 depuis ZPRIXBDA',
    )
