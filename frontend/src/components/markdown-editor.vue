<template>
  <el-row class="oj-markdown-editor"  :style="{ height: `${height}`, width: `${width}` }">
    <el-col :span="12" style="height: 100%;">
      <editor v-model="code" language="markdown" height="100%" width="100%"></editor>
    </el-col>
    <el-col :span="12" style="height: 100%;">
      <markdown :code="code" style="width: 100%; height: 100%; margin: 10px 10px;"></markdown>
    </el-col>
  </el-row>
</template>
  
<script>
import editor from './editor.vue';
import Markdown from './markdown.vue';

export default {
  components: { editor, Markdown },
  name: "MarkdownEditor",
  props: {
    code: {
      type: String,
      default: "",
    },
    height: {
      type: String,
      default: "300px",
    },
    width: {
      type: String,
      default: "100%",
    },
  },
  data() {
    return {
      code: "",
    };
  },
  methods: {},
  watch: {},
  model: {
    prop: ["code"],
  },
};
</script>