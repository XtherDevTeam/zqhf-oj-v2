<template>
  <div id="edit">
    <!-- dialogs -->
    <el-dialog width="50%" title="创建样例" :visible.sync="new_example_dialog_visible">
      此处为输入输出样例，不是数据文件上传处！<br>
      <el-container>
        <el-aside width="50%">
          <span>输入(.in)</span>
          <editor style="margin: 10px auto;" v-model="new_example_content['in']" @init="editorInit" lang="html"
                  theme="chrome"
                  width="100%" height="256px"></editor>
        </el-aside>
        <el-main style="padding: unset;">
          <span>输入(.out)</span>
          <editor style="margin: 10px auto;" v-model="new_example_content['out']" @init="editorInit" lang="html"
                  theme="chrome"
                  width="100%" height="256px"></editor>
        </el-main>
      </el-container>
      <span slot="footer" class="dialog-footer">
        <el-button @click="new_example_dialog_visible = false">取 消</el-button>
        <el-button type="primary"
                   @click="new_example_clicked">
          确 定
        </el-button>
      </span>
    </el-dialog>

    <el-dialog width="50%" title="修改样例" :visible.sync="edit_example_dialog_visible">
      此处为输入输出样例，不是数据文件上传处！<br>
      <el-container>
        <el-aside width="50%">
          <span>输入(.in)</span>
          <editor style="margin: 10px auto;" v-model="new_example_content['in']" @init="editorInit" lang="html"
                  theme="chrome"
                  width="100%" height="256px"></editor>
        </el-aside>
        <el-main style="padding: unset;">
          <span>输入(.out)</span>
          <editor style="margin: 10px auto;" v-model="new_example_content['out']" @init="editorInit" lang="html"
                  theme="chrome"
                  width="100%" height="256px"></editor>
        </el-main>
      </el-container>
      <span slot="footer" class="dialog-footer">
        <el-button @click="new_example_dialog_visible = false">取 消</el-button>
        <el-button type="primary"
                   @click="edit_example_clicked">
          确 定
        </el-button>
      </span>
    </el-dialog>


    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>编辑题目</span>
      </div>
      <el-input style="margin: 10px auto;" placeholder="请输入内容" v-model="problem_name">
        <template slot="prepend">标题</template>
      </el-input>
      <el-input style="margin: 10px auto;" placeholder="1000" v-model="problem_timeout">
        <template slot="prepend">超时限制</template>
      </el-input>
      <el-input style="margin: 10px auto;" placeholder="1000" v-model="problem_memory_limit">
        <template slot="prepend">空间限制</template>
      </el-input>

      <el-tag :key="tag" v-for="tag in problem_tags" closable :disable-transitions="false"
              @close="problem_tags_remove(tag)">
        {{ tag }}
      </el-tag>
      <el-input class="input-new-tag" v-if="problem_temp_tag_visible" v-model="problem_temp_tag_name"
                ref="saveTagInput" size="small" @keyup.enter.native="handleTagInputConfirm"
                @blur="handleTagInputConfirm" style="width: 256px;">
      </el-input>
      <el-button v-else class="button-new-tag" size="small" @click="problem_tag_visible_f">+ 新标签</el-button>
      <br>

      <div style="margin: 20px auto;"></div>
      <span style="margin: 20px auto;">题目介绍(可使用Markdown + KaTeX)</span>
      <editor style="margin: 10px auto;" v-model="problem_description" @init="editorInit" lang="html" theme="chrome"
              width="100%" height="256px"></editor>

      <el-table :data="problem_examples" style="width: 100%">
        <el-table-column fixed prop="in" label="输入" width="256"></el-table-column>
        <el-table-column fixed prop="out" label="输出" width="256"></el-table-column>
        <el-table-column fixed="right" label="操作">
          <template v-slot="scope">
            <el-button @click="edit_example_open(scope)" type="text" size="small">修改</el-button>
            <el-button @click="problem_remove_example(scope.$index)" type="text" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin: 20px auto;"></div>
      <el-button type="primary" @click="new_example_dialog_visible = true;">新建样例</el-button>
      <el-button type="primary" @click="submit_changes">提交更改</el-button>

      <div style="margin: 20px auto;"></div>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";

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
        if (response.data['data'] == null) {
          this.$message({
            type: "error",
            message: "题目内容拉取失败!"
          });
        } else {
          this.problem_name = response.data['data']['name'];
          this.problem_description = response.data['data']['description'];
          this.problem_timeout = response.data['data']['timeout'];
          this.problem_memory_limit = response.data['data']['memory'];
          this.problem_tags = JSON.parse(response.data['data']['tags']);
          this.problem_examples = JSON.parse(response.data['data']['examples']);
        }
      });
    },
    new_example_clicked() {
      this.problem_examples.push(this.new_example_content);
      this.new_example_content = {'in': '', 'out': ''};
      this.new_example_dialog_visible = false;
    },
    edit_example_clicked() {
      this.problem_examples[this.edit_example_index] = this.new_example_content;
      this.edit_example_index = -1;
      this.new_example_content = {'in': '', 'out': ''};
      this.edit_example_dialog_visible = false;
    },
    edit_example_open(scope) {
      this.edit_example_index = scope.$index;
      this.new_example_content = this.problem_examples[this.edit_example_index];
      this.edit_example_dialog_visible = true;
    },
    editorInit() {
      require('brace/ext/language_tools') //language extension prerequisite...
      require('brace/mode/html')
      require('brace/mode/javascript')    //language
      require('brace/mode/less')
      require('brace/theme/chrome')
      require('brace/snippets/javascript') //snippet
    },
    submit_changes() {
      axios.post('/api/v1/problems/edit/' + this.$route.query['id'], {
        name: this.problem_name,
        description: this.problem_description,
        timeout: parseInt(this.problem_timeout),
        memory_limit: parseInt(this.problem_memory_limit),
        tags: this.problem_tags,
        examples: this.problem_examples
      }).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: "error",
            message: "[" + response['code'] + "] " + response.data['text'] + " 上传题目失败"
          });
        } else {
          window.location = '/#/problems';
        }
      })
    },
    handleTagInputConfirm() {
      let inputValue = this.problem_temp_tag_name;
      if (inputValue) {
        this.problem_tags.push(inputValue);
      }
      this.problem_temp_tag_visible = false;
      this.problem_temp_tag_name = '';
    },
    problem_tags_remove(tag) {
      this.problem_tags.splice(this.problem_tags.indexOf(tag), 1);
    },
    problem_remove_example(index) {
      // rows.splice(index, 1);
      this.problem_examples.splice(index, 1);
    },
    problem_tag_visible_f() {
      this.problem_temp_tag_visible = true;
      this.$nextTick(_ => {
        this.$refs.saveTagInput.$refs.input.focus();
      });
    },
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      problem_name: "",
      problem_timeout: "",
      problem_memory_limit: "",
      problem_description: "",
      problem_tags: [],
      problem_examples: [],
      problem_temp_tag_visible: false,
      problem_temp_tag_name: "",
      new_example_dialog_visible: false,
      new_example_content: {'in': '', 'out': ''},
      edit_example_index: -1,
      edit_example_dialog_visible: false,
    }
  },
  components: {
    editor: require('vue2-ace-editor'),
  },
  mounted() {
    this.init();
  }
};
</script>

<style scoped>

</style>