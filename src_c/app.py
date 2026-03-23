#!/usr/bin/env python

from subprocess import CompletedProcess

from tadashi.apps import App
from tadashi.translators import Polly, Translator


class SNbone(App):
    def __init__(
        self,
        translator,
        compiler_options: list[str] = [],
        ephemeral: bool = False,
        populate_scops: bool = True,
    ):
        self.source = "./FGMRES_Threaded.c"
        self.run_args = ["1", "100", "30", "32", "1"]
        super().__init__(
            source=self.source,
            translator=translator,
            compiler_options=compiler_options,
            ephemeral=ephemeral,
            populate_scops=populate_scops,
        )

    def run_cmd(self):
        return ["./SNaCFE.x", *self.run_args]

    def codegen_init_args(self):
        return {"run_args": self.run_args}

    def extract_runtime(self, proc: CompletedProcess):
        lines = list(proc.stdout.decode().split("\n"))
        for idx, line in enumerate(lines):
            if "GFlops/s" in line:
                labels = line.replace("Est. ", "Est.").split()
                values = lines[idx + 1].split()
                gflopss = values[labels.index("Est.GFlops/s")]
                return 1.0 / float(gflopss)
                break
        raise Exception("Something wen't wronge while measuring")

    def compile_cmd(self, suffix: str):
        return ["make", "-B", "-j"]


def main():
    app = SNbone(translator=Polly())
    print(app.scops[0].schedule_tree[0].yaml_str)
    app.compile()
    print(f"{app.measure()=}")


if __name__ == "__main__":
    main()
    print("[DONE]")
