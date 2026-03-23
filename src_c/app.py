#!/usr/bin/env python

from tadashi.apps import App
from tadashi.translators import Polly, Translator


class SNbone(App):
    run_cmd: list[srt]

    def __init__(
        self,
        translator,
        compiler_options: list[str] = [],
        ephemeral: bool = False,
        populate_scops: bool = True,
    ):
        self.source = "./FGMRES_Threaded.c"
        super().__init__(
            source=self.source,
            translator=translator,
            compiler_options=compiler_options,
            ephemeral=ephemeral,
            populate_scops=populate_scops,
        )

    def run_cmd(self):
        return ["./SNaCFE.x"]

    def codegen_init_args(self):
        return {"run_cmd": self.run_cmd}

    def extract_runtime(self, stdout):
        print(f"{stdout=}")
        return 0.0

    def compile_cmd(self):
        return ["make"]


def main():
    app = SNbone(translator=Polly())
    print(app.scops[0].schedule_tree[0].yaml_str)
    app.compile()
    app.measure()


if __name__ == "__main__":
    main()
    print("[DONE]")
