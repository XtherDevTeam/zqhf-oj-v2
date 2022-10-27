<template>
  <div>
    <el-card shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>{{ article_content['name'] }}</span>
      </div>
      <span>作者: {{ article_content['author']['username'] }}</span>
      <div style="margin: 25px;"></div>
      <Markdown :code="article_content['text']"></markdown>
    </el-card>
    <div style="margin: 20px;"></div>
    <comment class="box-card" :area_id="'article:' + this.$route.query['id']"></comment>
  </div>
</template>

<script>
import axios from "axios";
import Comment from "~/components/comment";

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

      axios.get('/api/v1/articles/get/' + this.$route.query['id']).then((response) => {
        this.article_content = response.data['data'];
        if (this.article_content == null) {
          this.$message({
            type: "error",
            message: "文章内容拉取失败!"
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
      article_content: "",
      rendered_content: ""
    }
  },
  components: {
    comment: Comment,
    Markdown,
  }
};
</script>

<style scoped>
.box-card {
  width: 70%;
  margin: 0 auto;
}
</style>