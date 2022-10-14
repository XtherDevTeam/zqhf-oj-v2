<template>
  <div class="oj_comments_show_area">
    <el-card shadow="hover" class="oj_comments_post" v-if="logged_in">
      <div slot="header" class="clearfix">
        <span>发表评论</span>
      </div>
      <editor language="markdown" height="128px" v-model="post_comment_content"></editor>
      <el-button type="primary" @click="post_comment">提交评论</el-button>
    </el-card>
    <el-card shadow="hover" class="oj_comments_show" :key="index" v-for="comment, index in comments">
      <span>{{ comment['author']['username'] }}</span>
      <el-button style="float: right; padding: 3px 0" type="text"
                 @click="delete_comment(comment.index)"
                 v-if="logged_in && (user_info.data.id === comment.author.id || user_info.data['other_message']['permission_level'] === 2)">
        删除
      </el-button>
      <Markdown :code="comment['text']"></Markdown>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "~/components/editor.vue";
import Markdown from "~/components/markdown.vue";

export default {
  methods: {
    init() {
      
      if (this.area_id.indexOf("undefined") === -1) {
        axios
            .get("/api/v1/comments/get/" + this.area_id + '/' + this.comments_start + '/' + this.comments_limit, {
              params: {},
            })
            .then((response) => {
              if (response.data['code'] === 0) {
                this.comments = response.data['data'];
              } else {
                this.$message({
                  type: 'error',
                  message: '拉取评论区失败: ' + response.data['text'] + ' 如果评论区不存在，请联系管理员生成。'
                });
              }
            })
            .catch(function (error) {
              
            });
      }
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
    post_comment() {
      axios.post('/api/v1/comments/post/' + this.area_id, {text: this.post_comment_content})
          .then((response) => {
            if (response.data['code'] === 0) {
              this.post_comment_content = '### 支持Markdown哦~\n';
              this.init();
            } else {
              this.$message({
                type: 'error',
                message: '发布评论失败: ' + response.data.text
              });
            }
          })
    },
    delete_comment(id) {
      axios.post('/api/v1/comments/remove/' + this.area_id + '/' + id, {text: this.post_comment_content})
          .then((response) => {
            if (response.data['code'] === 0) {
              this.post_comment_content = '### 支持Markdown哦~\n';
              this.init();
            } else {
              this.$message({
                type: 'error',
                message: '删除评论失败: ' + response.data.text
              });
            }
          })
    },
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      comments_start: 0,
      comments_limit: 32,
      comments: {},
      post_comment_content: "### 支持Markdown哦~\n"
    }
  },
  props: {
    'area_id': {
      type: String,
      default: "area:not_exist",
    },
  },
  watch: {
    area_id(val) {
      this.area_id = val;
      this.init();
    }
  },
  mounted() {
    this.init();
  },
  components: {
    editor: MonacoEditor,
    Markdown,
  }
};
</script>

<style scoped>
.oj_comments_show {
  margin: 20px 0;
}
</style>