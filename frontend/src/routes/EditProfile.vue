<template>
  <el-card shadow="hover" class="box-card">
    <div slot="header" class="clearfix">
      <span>编辑个人信息</span>
    </div>
    <el-input placeholder="请输入内容" v-model="username">
      <template slot="prepend">用户名</template>
    </el-input>
    <el-input placeholder="简短的一句话~" v-model="introduction" style="margin: 10px auto;">
      <template slot="prepend">介绍</template>
    </el-input>
    <span style="margin: 10px auto;">长介绍(将显示在个人主页)</span>
    <editor style="margin: 10px auto;" v-model="full_introduction" language="markdown"
            width="100%" height="256px"></editor>
    <el-button type="primary" @click="submit_changes">提交</el-button>
    <div style="margin: 10px auto;"></div>
    <el-upload class="avatar-uploader" action="/api/v1/user/image/upload"
               :show-file-list="false"
               :on-success="uploadImageSuccess"
               :before-upload="beforeImageUpload">
      <i class="el-icon-plus avatar-uploader-icon"></i>
      <div slot="tip" class="el-upload__tip">上传用户头像(仅jpeg格式)</div>
    </el-upload>
  </el-card>
</template>

<script>
import axios from "axios";
import MonacoEditor from "../components/editor.vue";
import 'mavon-editor/dist/css/index.css'

export default {
  methods: {
    init() {
      console.log(this.user_info);
      axios.get("/api/v1/user/details", {
        params: {},
      }).then((response) => {
        this.user_info = response.data;
        this.logged_in = response.data['code'] === 0;
        this.username = response.data['data']['username'];
        this.introduction = response.data['data']['introduction'];
        this.full_introduction = response.data['data']['full_introduction'];
      }).catch(function (error) {
        console.log(error);
      });
    },

    submit_changes() {
      axios.post('/api/v1/user/change_info', {
        'username': this.username,
        'introduction': this.introduction,
        'full_introduction': this.full_introduction
      }).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: "error",
            message: "[" + response['code'] + "] " + response.data['text'] + " 上传用户信息失败"
          });
        } else {
          window.location = '/#/';
        }
      })
    },
    beforeImageUpload(file) {
      const isJPG = file.type === 'image/jpeg';
      const isLt2M = file.size / 1024 / 1024 < 2;

      if (!isJPG) {
        this.$message.error('上传头像图片只能是 JPG 格式!');
      }
      if (!isLt2M) {
        this.$message.error('上传头像图片大小不能超过 2MB!');
      }
      return isJPG && isLt2M;
    },
    uploadImageSuccess(res, file) {
      this.imageUrl = URL.createObjectURL(file.raw);
      window.location = '/#/profile';
    }
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      edit_content: "",
      username: "",
      introduction: "",
      full_introduction: "",
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
.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
}
</style>