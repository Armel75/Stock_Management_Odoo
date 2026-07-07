{
    'name': 'Consultation Stocks et Prix SAGE X3',
    'version': '1.0.0',
    'category': 'Inventory/Stock',
    'summary': "Synchronisation quotidienne des stocks et prix depuis SAGE X3 (SQL Server) vers Odoo 17 (PostgreSQL)",
    'description': """
Module de consultation des stocks et prix des articles.
========================================================

Architecture technique :
- Repository : Connexion et extraction depuis les vues SQL Server de SAGE X3
- Services : Logique métier de synchronisation et transformation
- Modèles : Cache de données en PostgreSQL pour consultation rapide

Fonctionnalités :
- Synchronisation quotidienne automatique (ETL) à 00h00
- Consultation des articles, stocks et prix sur PostgreSQL
- Historique de synchronisation et monitoring
- Configuration de la connexion SQL Server depuis l'interface
    """,
    'author': 'Votre Société',
    'website': '',
    'depends': ['base', 'web'],
    'data': [
        'security/x3_stock_security.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter_data.xml',
        'views/login_layout.xml',
        'views/x3_article_cache_views.xml',
        'views/x3_sync_history_views.xml',
        'views/x3_sync_configuration_views.xml',
        'views/x3_manual_sync_wizard_views.xml',
        'views/x3_tariff_littoral_views.xml',
        'views/x3_tariff_bamenda_views.xml',
        'views/x3_tariff_centre_views.xml',
        'views/x3_tariff_ouest_views.xml',
        'views/x3_tariff_kribi_views.xml',
        'views/x3_tariff_bertoua_views.xml',
        'views/x3_tariff_ngaoundere_views.xml',
        'views/menu_views.xml',
        'views/res_users_views.xml',
        'cron/sync_cron.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
