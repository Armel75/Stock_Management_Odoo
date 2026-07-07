import logging

from odoo import models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class X3ManualSyncWizard(models.TransientModel):
    """
    Wizard pour lancer une synchronisation manuelle.
    Accessible uniquement aux administrateurs.
    """
    _name = 'x3.manual.sync.wizard'
    _description = 'Synchronisation manuelle des stocks et prix'

    def action_launch_sync(self):
        """
        Lance la synchronisation directement.
        Les données sont commitées au fur et à mesure :
        même en cas de timeout, les articles sont en base.
        Le cron de secours rattrape si besoin.
        """
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('x3_stock.sync_pending', 'True')
        self.env.cr.commit()

        service = self.env['x3.sync.service']
        result = service.run_full_sync()

        if result.get('success'):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Synchronisation terminée',
                    'message': result.get('message', 'Succès.'),
                    'type': 'success',
                    'sticky': False,
                },
            }
        else:
            raise UserError(
                f"Erreur lors de la synchronisation :\n{result.get('message', 'Erreur inconnue')}"
            )