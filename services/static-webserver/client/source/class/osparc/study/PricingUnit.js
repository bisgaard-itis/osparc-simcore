/* ************************************************************************

   osparc - the simcore frontend

   https://osparc.io

   Copyright:
     2023 IT'IS Foundation, https://itis.swiss

   License:
     MIT: https://opensource.org/licenses/MIT

   Authors:
     * Odei Maiz (odeimaiz)

************************************************************************ */

qx.Class.define("osparc.study.PricingUnit", {
  extend: qx.ui.core.Widget,
  type: "abstract",

  construct: function(pricingUnit) {
    this.base(arguments);

    this._setLayout(new qx.ui.layout.VBox(5));

    this.set({
      padding: 10,
      decorator: "rounded",
      minWidth: 100,
      allowGrowX: false,
      allowGrowY: false,
    });

    this.setUnitData(pricingUnit);

    osparc.utils.Utils.addBorder(this);
  },

  events: {
    "editPricingUnit": "qx.event.type.Event",
  },

  properties: {
    selected: {
      check: "Boolean",
      init: false,
      nullable: false,
      event: "changeSelected",
      apply: "__applySelected",
    },

    unitData: {
      check: "osparc.data.model.PricingUnit",
      nullable: false,
      init: null,
      apply: "_buildLayout"
    },

    showEditButton: {
      check: "Boolean",
      init: false,
      nullable: true,
      event: "changeShowEditButton"
    },
  },

  members: {
    _createChildControlImpl: function(id) {
      let control;
      switch (id) {
        case "name":
          control = new qx.ui.basic.Label().set({
            font: "text-16"
          });
          this._add(control);
          break;
        case "price":
          control = new qx.ui.basic.Label().set({
            font: "text-14"
          });
          this._add(control);
          break;
        case "edit-button":
          control = new qx.ui.form.Button(qx.locale.Manager.tr("Edit"));
          this.bind("showEditButton", control, "visibility", {
            converter: show => show ? "visible" : "excluded"
          });
          control.addListener("execute", () => this.fireEvent("editPricingUnit"));
          this._add(control);
          break;
      }
      return control || this.base(arguments, id);
    },

    _buildLayout: function(pricingUnit) {
      this._removeAll();

      const name = this.getChildControl("name");
      pricingUnit.bind("name", name, "value");
    },

    __applySelected: function(selected) {
      const strong = qx.theme.manager.Color.getInstance().resolve("strong-main");
      osparc.utils.Utils.updateBorderColor(this, selected ? strong : "transparent");
    },
  }
});
