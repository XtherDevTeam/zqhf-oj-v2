<template>
  <div
    class="monaco-editor-container"
    :style="{ height: `${height}`, width: `${width}` }"
    ref="container"
  ></div>
</template>

<script>
import * as monaco from "monaco-editor";

export default {
  name: "MyCodeEditor",
  props: {
    height: {
      type: String,
      default: "300px",
    },
    width: {
      type: String,
      default: "100%",
    },
    code: String,
    language: {
      type: String,
      default: "json",
    },
    readonly: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      monacoEditor: undefined,
      themeMedia: {},
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
          fontFamily: 'Fira Mono'
        });
        monaco.editor.remeasureFonts();
        
        this.monacoEditor.onDidChangeModelContent((e) => {
          this.$emit("change", this.monacoEditor.getValue());
        });

        this.themeMedia = window.matchMedia("(prefers-color-scheme: light)");
        this.themeMedia.onchange = (e) => {
          if (e.matches) {
            monaco.editor.setTheme("vs");
          } else {
            monaco.editor.setTheme("vs-dark");
          }
        };
        if (this.themeMedia.matches) {
          monaco.editor.setTheme("vs");
        } else {
          monaco.editor.setTheme("vs-dark");
        }
      });
    },
  },
  watch: {
    language(val) {
      monaco.editor.setModelLanguage(this.monacoEditor.getModel(), val);
    },
    code(val) {
      if (this.monacoEditor.getValue() !== val) {
        this.monacoEditor.setValue(val);
        this.$emit("change", this.monacoEditor.getValue());
      }
    },
  },
  model: {
    prop: ["code"],
    event: ["change"],
  },
};
</script>

<style scoped lang="scss">
.monaco-editor-container {
  width: 100%;
  overflow: hidden;
}
</style>
