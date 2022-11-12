<template>
  <div style="width: 90%;margin: 0 auto;">
    <el-card shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>出错啦！</span>
      </div>
      <div style="text-align: center;">
        您的页面在传输过程中被 jerry_chou 的垃圾服务器当成同类丢掉了。<br/>
        <img src="../assets/404.png"/>
      </div>
    </el-card>
  </div>
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
      logged_in: ""
    }
  }
};
</script>

<style scoped>

</style>