Component({
  properties: {
    visible: {
      type: Boolean,
      value: false
    },
    adData: {
      type: Object,
      value: {}
    }
  },

  methods: {
    onAdClick() {
      const { linkUrl } = this.data.adData;
      if (linkUrl) {
        wx.navigateTo({
          url: linkUrl
        });
      }
    },

    onClose() {
      this.triggerEvent('close');
    }
  }
}); 