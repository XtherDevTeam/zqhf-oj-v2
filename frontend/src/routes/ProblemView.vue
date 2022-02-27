<template>
  <el-card shadow="hover" class="box-card">
    <div slot="header" class="clearfix">
      <span>{{ problem_content['name'] }}</span><br>
      <span>作者: {{ problem_content['author'] }}</span>
      <span>内存限制: {{ problem_content['memory'] }} kb</span>
      <span>时间限制: {{ problem_content['timeout'] }} ms</span>
    </div>
    <span><strong>题目介绍: </strong></span><br>
    <div style="margin: 10px auto;"></div>
    <div class="markdown-body" id="markdownRenderedPlace" v-html="rendered_content"></div>

    <div style="margin: 10px auto;"></div>

    <span><strong>题目样例: </strong></span><br>
    <div style="margin: 10px auto;"></div>
    <div v-for="example in problem_content['examples']">
      <el-container>
        <el-aside width="50%">
          输入:<br>
          <pre><code>{{ example['in'] }}</code>
          </pre>
        </el-aside>
        <el-main style="padding: unset;">
          输出:<br>
          <pre>
<code>
{{ example['out'] }}
</code>
          </pre>
        </el-main>
      </el-container>
    </div>
  </el-card>
</template>

<script>
import axios from "axios";

const markdown = require('markdown-it')(),
    markdown_with_katex = require('markdown-it-katex');

markdown.use(markdown_with_katex)


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

      axios.get('/api/v1/problems/get/' + this.$route.query['id']).then((response) => {
        this.problem_content = response.data['data'];
        if (this.problem_content == null) {
          this.$message({
            type: "error",
            message: "题目内容拉取失败!"
          });
        } else {
          this.problem_content['tags'] = JSON.parse(this.problem_content['tags']);
          this.problem_content['examples'] = JSON.parse(this.problem_content['examples']);
          this.rendered_content = markdown.render(this.problem_content['description']);
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
      problem_content: "",
      rendered_content: "",
      app_name: this.$parent.$parent.$parent.app_name,
    }
  }
};
</script>

<style scoped>
.box-card {
  width: 70%;
  margin: 0 auto;
}
</style>