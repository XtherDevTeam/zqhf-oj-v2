<template>
  <div>
    <el-card shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>{{ problem_list_content['name'] }}</span>
      </div>
      <span><strong>题单介绍: </strong></span><br>
      <div style="margin: 10px auto;"></div>
      <div class="markdown-body" id="markdownRenderedPlace" v-html="rendered_description_content"></div>
      <div style="margin: 10px auto;"></div>
      <el-table :data="problem_list_content['problems']" style="width: 100%">
        <el-table-column prop="id" fixed="right" label="题目编号" width="100px"></el-table-column>
        <el-table-column prop="name" fixed="right" label="题目标题"></el-table-column>

        <el-table-column fixed="right" label="操作">
          <template v-slot="scope">
            <el-button @click="goto_problem(scope.row.id)" type="text" size="small">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <comment style="margin: 10px auto;" class="box-card" :area_id="'problem_list:' + this.problem_list_content.id"></comment>
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "../components/editor.vue";
import Comment from "../components/comment";

import markdownItHighlight from 'markdown-it-highlight';

const markdown = require('markdown-it')(),
    markdown_with_katex = require('@iktakahiro/markdown-it-katex');

markdown.use(markdownItHighlight);
markdown.use(markdown_with_katex);


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

      axios.get('/api/v1/problem_lists/get/' + this.$route.query['id']).then((response) => {
        this.problem_list_content = response.data['data'];
        if (this.problem_list_content == null) {
          this.$message({
            type: "error",
            message: "题单内容拉取失败!"
          });
        } else {
          this.rendered_description_content = markdown.render(this.problem_list_content['description']);
        }
      });
    },
    goto_problem(id) {
      window.location = '/#/problems/view?id=' + id;
    },
  },
  mounted() {
    this.init();
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      problem_list_content: "",
      rendered_description_content: ""
    }
  },
  components: {
    comment: Comment
  }
};
</script>

<style scoped>
.box-card {
  width: 70%;
  margin: 0 auto;
}
</style>