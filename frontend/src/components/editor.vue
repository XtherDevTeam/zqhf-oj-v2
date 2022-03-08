<template>
  <div class="monaco-editor-container" :style="{ height: `${height}`, width: `${width}` }" ref="container"></div>
</template>

<script>
import * as monaco from "monaco-editor";

export default {
  name: "MyCodeEditor",
  props: {
    'height': {
      type: String,
      default: "300px",
    },
    'width': {
      type: String,
      default: "100%",
    },
    'code': String,
    'language': {
      type: String,
      default: "json",
    },
    ':readonly': {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      theme: "vs",
      monacoEditor: undefined,
    };
  },
  created() {
    this.initEditor();
  },
  methods: {
    initEditor() {
      this.$nextTick(() => {
        this.monacoEditor = monaco.editor.create(this.$refs.container, {
          value: this.code,
          readonly: this.readonly,
          theme: this.theme,
          language: this.language,
          automaticLayout: true,
        });
        this.monacoEditor.onDidChangeModelContent((e) => {
          this.$emit('changed', this.monacoEditor.getValue());
        });
      });
    }
  },
  watch: {
    language(val) {
      monaco.editor.setModelLanguage(this.monacoEditor.getModel(), val);
    },
    code(val) {
      if (this.monacoEditor.getValue() !== val) {
        this.monacoEditor.setValue(val);
      }
    }
  },
  model: {
    prop: ['code'],
    event: ['changed']
  }
};
</script>

<style scoped lang="scss">
.monaco-editor-container {
  width: 100%;
  overflow: hidden;
}
</style>
