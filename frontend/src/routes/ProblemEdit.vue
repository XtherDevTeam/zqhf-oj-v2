<template>
  <div id="edit">
    <!-- dialogs -->
    <el-dialog width="90%" title="创建样例" :visible.sync="new_example_dialog_visible">
      此处为输入输出样例，不是数据文件上传处！<br>
      <el-container>
        <el-aside width="50%">
          <span>输入(.in)</span>
          <editor style="margin: 10px auto;" v-model="new_example_content['in']" language="markdown"

                  width="100%" height="256px"></editor>
        </el-aside>
        <el-main style="padding: unset;">
          <span>输出(.out)</span>
          <editor style="margin: 10px auto;" v-model="new_example_content['out']" language="markdown"

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
    <el-dialog width="90%" title="修改样例" :visible.sync="edit_example_dialog_visible">
      此处为输入输出样例，不是数据文件上传处！<br>
      <el-container>
        <el-aside width="50%">
          <span>输入(.in)</span>
          <editor style="margin: 10px auto;" v-model="new_example_content['in']" language="markdown"

                  width="100%" height="256px"></editor>
        </el-aside>
        <el-main style="padding: unset;">
          <span>输出(.out)</span>
          <editor style="margin: 10px auto;" v-model="new_example_content['out']" language="markdown"

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
    <el-dialog width="90%" title="修改数据点" :visible.sync="edit_checkpoint_dialog_visible">
      <span>{{ edit_checkpoint_mode === "in" ? "修改输入(.in)" : "修改输出(.out)" }}</span><br>
      <el-upload
          name="file" drag
          :action="edit_checkpoint_upload_url"
          show-file-list="false">
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <div class="el-upload__tip" slot="tip">上传一个.{{ edit_checkpoint_mode }}文件</div>
      </el-upload>

      <span slot="footer" class="dialog-footer">
        <el-button @click="edit_checkpoint_dialog_visible = false">取 消</el-button>
        <el-button type="primary"
                   @click="refresh_checkpoint_list();edit_checkpoint_dialog_visible = false;">
          确 定
        </el-button>
      </span>
    </el-dialog>

    <el-dialog title="批量上传文件" :visible.sync="upload_file_dialog_visible">
      <el-upload name="file" multiple drag :action="upload_file_url">
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">上传任意.in, .out文件, 将文件拖到此处, 或<em>点击上传</em></div>
      </el-upload>
      <span slot="footer" class="dialog-footer">
        <el-button @click="edit_checkpoint_dialog_visible = false">取 消</el-button>
        <el-button type="primary"
                   @click="refresh_checkpoint_list();edit_checkpoint_dialog_visible = false;">
          确 定
        </el-button>
      </span>
    </el-dialog>

    <el-dialog title="上传数据点" :visible.sync="new_checkpoint_dialog_visible">
      <span>上传数据点</span><br>
      <el-upload name="file" drag :action="new_checkpoint_upload_url_input" show-file-list="false">
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">上传一个.in文件, 将文件拖到此处, 或<em>点击上传</em></div>
      </el-upload>
      <el-upload
          name="file" drag
          :action="new_checkpoint_upload_url_output"
          show-file-list="false">
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">上传一个.out文件, 将文件拖到此处, 或<em>点击上传</em></div>
      </el-upload>

      <span slot="footer" class="dialog-footer">
        <el-button @click="new_checkpoint_dialog_visible = false">取 消</el-button>
        <el-button type="primary"
                   @click="init();new_checkpoint_dialog_visible = false;">
          确 定
        </el-button>
      </span>
    </el-dialog>


    <el-card shadow="hover" class="box-card">
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

      <div style="margin: 20px auto;"></div>
      <span style="margin: 20px auto;">设置解禁时间</span>
      <el-date-picker
        value-format="timestamp"
        v-model="problem_appear_time"
        type="datetime"
        placeholder="设置解禁时间">
      </el-date-picker>
      <div style="margin: 20px auto;"></div>

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
      <span style="margin: 20px auto;">题目介绍(可使用Markdown + LaTeX)</span>
      <MarkdownEditor style="margin: 10px auto;" v-model="problem_description" language="markdown"
              width="100%" height="256px"></MarkdownEditor>

      <span style="margin: 10px auto;">Special Judge 配置(请使用C++代码编写)</span>
      <editor style="margin: 10px auto;" v-model="problem_special_judge_code" language="cpp"
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

      <el-table :data="problem_checkpoint_list" style="width: 100%">
        <el-table-column fixed label="检查点名">
          <template v-slot="scope">{{ scope.row }}</template>
        </el-table-column>
        <el-table-column fixed="right" label="操作">
          <template v-slot="scope">
            <el-button @click="edit_checkpoint_input_open(scope)" type="text" size="small">上传输入</el-button>
            <el-button @click="edit_checkpoint_output_open(scope)" type="text" size="small">上传输出</el-button>
            <el-button @click="remove_checkpoint(scope)" type="text" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin: 20px auto;"></div>
      <el-input placeholder="" v-model="new_checkpoint_name" style="width: 256px;">
        <template slot="prepend">名称</template>
      </el-input>
      <el-button type="primary" @click="upload_new_checkpoint">上传新测试点</el-button>
      <el-button type="primary" @click="upload_file">批量上传文件</el-button>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "~/components/editor.vue";
import MarkdownEditor from '../components/markdown-editor.vue';

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

      axios.get('/api/v1/problems/get/' + this.$route.query['id']).then((response) => {
        if (response.data['data'] == null) {
          this.$message({
            type: "error",
            message: "题目内容拉取失败!"
          });
        } else {
          this.problem_name = response.data['data']['name'];
          this.problem_description = response.data['data']['description'];
          this.problem_special_judge_code = response.data['data']['special_judge_code'];
          this.problem_timeout = response.data['data']['timeout'];
          this.problem_memory_limit = response.data['data']['memory'];
          this.problem_tags = JSON.parse(response.data['data']['tags']);
          this.problem_examples = JSON.parse(response.data['data']['examples']);
          this.problem_appear_time = response.data['data']['appear_time'] * 1000;
          console.log('-wdnmd', response.data['data']['appear_time'])
        }
      });
    },
    refresh_checkpoint_list() {
      this.new_checkpoint_upload_url_output = "";
      this.new_checkpoint_upload_url_input = "";
      this.edit_checkpoint_upload_url = "";
      this.new_checkpoint_name = "";
      axios.get('/api/v1/problems/checkpoints/get-list/' + this.$route.query['id']).then((response) => {
        if (response.data['data'] == null) {
          this.$message({
            type: "error",
            message: "题目测试点列表拉取失败!"
          });
        } else {
          this.problem_checkpoint_list = response.data['data'];
        }
      });
    },
    edit_checkpoint_input_open(scope) {
      this.edit_checkpoint_mode = "in";

      this.edit_checkpoint_upload_url = '/api/v1/problems/checkpoints/upload/' +
          this.$route.query['id'] + '/' + scope.row + '/' + this.edit_checkpoint_mode;

      this.edit_checkpoint_dialog_visible = true;
    },
    edit_checkpoint_output_open(scope) {
      this.edit_checkpoint_mode = "out";

      this.edit_checkpoint_upload_url = '/api/v1/problems/checkpoints/upload/' +
          this.$route.query['id'] + '/' + scope.row + '/' + this.edit_checkpoint_mode;

      this.edit_checkpoint_dialog_visible = true;
    },
    upload_new_checkpoint() {
      this.new_checkpoint_upload_url_input = '/api/v1/problems/checkpoints/upload/' +
          this.$route.query['id'] + '/' + this.new_checkpoint_name + '/in';

      this.new_checkpoint_upload_url_output = '/api/v1/problems/checkpoints/upload/' +
          this.$route.query['id'] + '/' + this.new_checkpoint_name + '/out';

      this.new_checkpoint_dialog_visible = true;
    },
    remove_checkpoint(scope) {
      axios.post('/api/v1/problems/checkpoints/remove/' + this.$route.query['id'] + '/' + scope.row, {})
          .then((response) => {
            if (response.data['code'] !== 0) {
              this.$message({
                type: "error",
                message: "[" + response['code'] + "] " + response.data['text'] + " 删除题目测试点失败"
              });
            }
            this.refresh_checkpoint_list();
          })
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

    submit_changes() {
      axios.post('/api/v1/problems/edit/' + this.$route.query['id'], {
        name: this.problem_name,
        description: this.problem_description,
        timeout: parseInt(this.problem_timeout),
        memory_limit: parseInt(this.problem_memory_limit),
        tags: this.problem_tags,
        examples: this.problem_examples,
        special_judge_code: this.problem_special_judge_code,
        appear_time: (this.problem_appear_time / 1000) | 0
      }).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: "error",
            message: "[" + response['code'] + "] " + response.data['text'] + " 上传题目失败"
          });
        } else {
          this.$router.back();
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
    upload_file() {
      this.upload_file_dialog_visible = true;
      this.upload_file_url = '/api/v1/problems/checkpoints/upload/' +
          this.$route.query['id'] + '/file';
    }
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
      problem_special_judge_code: "",
      problem_temp_tag_visible: false,
      problem_temp_tag_name: "",
      problem_checkpoint_list: [],
      problem_appear_time: 0,
      new_example_dialog_visible: false,
      new_example_content: {'in': '', 'out': ''},
      edit_example_index: -1,
      edit_example_dialog_visible: false,
      edit_checkpoint_dialog_visible: false,
      edit_checkpoint_mode: "in",
      edit_checkpoint_name: "",
      edit_checkpoint_upload_url: "",
      new_checkpoint_dialog_visible: false,
      upload_file_dialog_visible: false,
      upload_file_url: "",
      upload_file_name: "",
      new_checkpoint_upload_url_input: "",
      new_checkpoint_upload_url_output: "",
      new_checkpoint_name: ""
    }
  },
  components: {
    editor: MonacoEditor,
    MarkdownEditor: MarkdownEditor,
  },
  mounted() {
    this.init();
    this.refresh_checkpoint_list();
  }
};
</script>

<style scoped>

</style>