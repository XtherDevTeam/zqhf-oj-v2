<template>
  <el-card shadow="hover" class="box-card">
    <div slot="header" class="clearfix">
      <span>{{ bulletin_content['name'] }}</span>
    </div>
    <span>上次修改: {{ bulletin_content['time'] }}</span>
    <div style="margin: 50px;"></div>
    <Markdown :code="bulletin_content['content']"></markdown>
  </el-card>
</template>

<script>
import axios from "axios";
import Markdown from "~/components/markdown.vue";

export default {
  methods: {
    init() {
      
      axios.get("/api/v1/user/details", {
        params: {},
      }).then((response) => {
        this.user_info = response.data;
        this.logged_in = response.data['code'] === 0;
      }).catch(function (error) {
        
      });

      axios.get('/api/v1/bulletins/get/' + this.$route.query['id']).then((response) => {
        this.bulletin_content = response.data['data'];
        if (this.bulletin_content == null) {
          this.$message({
            type: "error",
            message: "公告内容拉取失败!"
          });
        }
      });
    },

  },
  mounted() {
    this.init();
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      bulletin_content: "",
    }
  },
  components: {
    Markdown: Markdown
  }
};
</script>

<style scoped>
.box-card {
  width: 70%;
  margin: 0 auto;
}
</style>