<template>
  <el-card shadow="hover" class="box-card">
    <div slot="header" class="clearfix">
      <span>编辑公告</span>
    </div>
    <el-input placeholder="请输入内容" v-model="bulletin_name">
      <template slot="prepend">标题</template>
    </el-input>
    <div style="margin: 10px auto;"></div>
    <span style="margin: 10px auto;">公告内容</span>
    <editor style="margin: 10px auto;" v-model="bulletin_content" language="markdown" theme="chrome"
            width="100%" height="256px"></editor>
    <el-button type="primary" @click="submit_changes">提交</el-button>
  </el-card>
</template>

<script>
import axios from "axios";
import MonacoEditor from "../components/editor.vue";

export default {
  methods: {
    init() {
      console.log(this.user_info);
      axios.get("/api/v1/user/details", {
        params: {},
      }).then((response) => {
        this.user_info = response.data;
        this.logged_in = response.data['code'] === 0;
      }).catch(function (error) {
        console.log(error);
      });

      axios.get('/api/v1/bulletins/get/' + this.$route.query['id']).then((response) => {
        if (response.data['data'] == null) {
          this.$message({
            type: "error",
            message: "公告内容拉取失败!"
          });
        } else {
          this.bulletin_name = response.data['data']['name'];
          this.bulletin_content = response.data['data']['content'];
        }
      });
    },

    submit_changes() {
      axios.post('/api/v1/bulletins/edit/' + this.$route.query['id'], {
        'name': this.bulletin_name,
        'content': this.bulletin_content
      }).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: "error",
            message: "[" + response['code'] + "] " + response.data['text'] + " 上传公告失败"
          });
        } else {
          window.location = '/#/';
        }
      })
    }
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      edit_content: "",
      bulletin_name: "",
      bulletin_content: "",
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