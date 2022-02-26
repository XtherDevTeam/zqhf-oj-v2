<template>

</template>

<script>
import axios from "axios";


export default {
  methods: {
    init() {
      console.log(this.user_info);
      axios
          .get("/api/v1/user/details", {
            params: {},
          })
          .then((response) => {
            this.user_info = response.data;
            this.logged_in = response.data['code'] === 0;
          })
          .catch(function (error) {
            console.log(error);
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