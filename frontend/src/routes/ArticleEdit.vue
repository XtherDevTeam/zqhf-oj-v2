<template>
  <el-card shadow="hover" class="box-card">
    <div slot="header" class="clearfix">
      <span>编辑文章</span>
    </div>
    <el-input placeholder="请输入内容" v-model="article_name">
      <template slot="prepend">标题</template>
    </el-input>
    <div style="margin: 10px auto;"></div>
    <span style="margin: 10px auto;">文章内容</span>
    <editor style="margin: 10px auto;" v-model="article_content" language="markdown"
            width="100%" height="256px"></editor>
    <el-radio v-model="article_visible" label="true">对所有人可见</el-radio>
    <el-radio v-model="article_visible" label="false">对自己可见</el-radio>
    <el-button type="primary" @click="submit_changes">提交</el-button>
  </el-card>
</template>

<script>
import axios from "axios";
import MonacoEditor from "../components/editor.vue";

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
        if (response.data['data'] == null) {
          this.$message({
            type: "error",
            message: "文章内容拉取失败!"
          });
        } else {
          this.article_name = response.data['data']['name'];
          this.article_content = response.data['data']['text'];
          this.article_visible = response.data['data']['visible'] ? "true" : "false";
        }
      });
    },

    submit_changes() {
      axios.post('/api/v1/articles/edit/' + this.$route.query['id'], {
        'name': this.article_name,
        'text': this.article_content,
        'visible': this.article_visible === "true",
      }).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: "error",
            message: "[" + response['code'] + "] " + response.data['text'] + " 上传文章失败"
          });
        } else {
          window.location = '/#/articles';
        }
      })
    }
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      edit_content: "",
      article_name: "",
      article_content: "",
      article_visible: "false",
    }
  },
  components: {
    editor: MonacoEditor,
  },
  mounted() {
    this.init();
  }
};
</script>

<style scoped>

</style>