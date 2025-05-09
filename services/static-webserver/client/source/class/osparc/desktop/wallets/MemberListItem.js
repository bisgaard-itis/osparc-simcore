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

qx.Class.define("osparc.desktop.wallets.MemberListItem", {
  extend: osparc.ui.list.ListItemWithMenu,

  properties: {
    gid: {
      check: "Number",
      init: null,
      nullable: false,
      event: "changeGid"
    }
  },

  events: {
    "promoteToAccountant": "qx.event.type.Data",
    "demoteToMember": "qx.event.type.Data",
    "removeMember": "qx.event.type.Data"
  },

  members: {
    // overridden
    _applySubtitleMD: function(value) {
      this.base(arguments, value);

      // highlight me
      const email = osparc.auth.Data.getInstance().getEmail();
      if (value && value.includes(email)) {
        this.addState("selected");
      }
    },

    // overridden
    _setRole: function() {
      const accessRights = this.getAccessRights();
      const role = this.getChildControl("role");
      if ("getWrite" in accessRights && accessRights.getWrite()) {
        role.setValue(osparc.data.Roles.WALLET["write"].label);
      } else if ("getRead" in accessRights && accessRights.getRead()) {
        role.setValue(osparc.data.Roles.WALLET["read"].label);
      }
    },

    // overridden
    _getOptionsMenu: function() {
      const menu = new qx.ui.menu.Menu().set({
        position: "bottom-right"
      });

      const options = this.getOptions();
      if (options === null) {
        return menu;
      }

      if (options.includes("promoteToAccountant")) {
        const promoteButton = new qx.ui.menu.Button(this.tr("Promote to ") + osparc.data.Roles.WALLET["write"].label);
        promoteButton.addListener("execute", () => {
          this.fireDataEvent("promoteToAccountant", {
            gid: this.getGid(),
            name: this.getTitle()
          });
        });
        menu.add(promoteButton);
      }
      if (options.includes("demoteToMember")) {
        const demoteButton = new qx.ui.menu.Button(this.tr("Demote to ") + osparc.data.Roles.WALLET["read"].label);
        demoteButton.addListener("execute", () => {
          this.fireDataEvent("demoteToMember", {
            gid: this.getGid(),
            name: this.getTitle()
          });
        });
        menu.add(demoteButton);
      }

      if (menu.getChildren().length) {
        menu.addSeparator();
      }

      if (options.includes("removeMember")) {
        const accessRights = this.getAccessRights();
        let currentRole = osparc.data.Roles.WALLET["read"];
        if (accessRights.getWrite()) {
          currentRole = osparc.data.Roles.WALLET["write"];
        }
        const removeButton = new qx.ui.menu.Button(this.tr("Remove ") + currentRole.label).set({
          textColor: "danger-red"
        });
        removeButton.addListener("execute", () => {
          this.fireDataEvent("removeMember", {
            gid: this.getGid(),
            name: this.getTitle()
          });
        });
        menu.add(removeButton);
      }

      return menu;
    }
  }
});
