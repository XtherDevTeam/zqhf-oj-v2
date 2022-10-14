<template>

</template>

<script>
import axios from "axios";
import MonacoEditor from "~/components/editor.vue";


export default {
  methods: {
    init() {
      
      axios
          .get("/api/v1/user/details", {
            params: {},
          })
          .then((response) => {
            this.user_info = response.data;
            this.logged_in = response.data['code'] === 0;
          })
          .catch(function (error) {
            
          });
    },

  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      app_name: this.$parent.$parent.$parent.app_name
    }
  }
};
</script>

<style scoped>

</style>