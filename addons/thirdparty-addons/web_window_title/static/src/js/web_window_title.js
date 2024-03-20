/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";

patch(WebClient.prototype, {
    /**
     * @override
     */
    setup() {
        const title = document.title;
        super.setup();
        this.title.setParts({ zopenerp: title });
    },
});
