<template>
  <h3>未找到页面!</h3>
</template>

<script>
import axios from "axios";
import MonacoEditor from "../components/editor.vue";


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
      logged_in: ""
    }
  }
};
</script>

<style scoped>

</style>