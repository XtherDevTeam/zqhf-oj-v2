<template>
  <div>
    <div>
        <MarkdownEditor v-model="code"></MarkdownEditor>
        <div v-html="code">
        </div>
    </div>
    <div>
      <el-checkbox v-model="changable">Changable: </el-checkbox>
      <problems-shower v-model="problem_list" :changable="changable"></problems-shower>
    </div>  
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "~/components/editor.vue";
import markdownEditor from '../components/markdown-editor.vue';
import ProblemsShower from '../components/problems-shower.vue';

export default {
  components: { MarkdownEditor: markdownEditor, ProblemsShower },
  methods: {
    init() {
    }
  },
  data() {
    return {
      code: "nothing",
      problem_list: [],
      changable: false,
    }
  }
};
</script>

<style scoped>

</style>