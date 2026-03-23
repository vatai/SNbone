#!/usr/bin/env python

import logging
from pathlib import Path
from subprocess import CompletedProcess

from tadashi.apps import App
from tadashi.translators import Polly, Translator


class SNbone(App):
    def __init__(
        self,
        run_args=["1", "100", "30", "32", "1"],
        source=Path(__file__).parent / "./FGMRES_Threaded.c",
        translator: Translator = None,
        compiler_options: list[str] = [],
        ephemeral: bool = False,
        populate_scops: bool = True,
    ):

        self.logger = logging.getLogger(__name__)
        self.source = source
        self.run_args = run_args
        super().__init__(
            source=self.source,
            translator=translator,
            compiler_options=compiler_options,
            ephemeral=ephemeral,
            populate_scops=populate_scops,
        )

    def codegen_init_args(self):
        return {"run_args": self.run_args}

    def run_cmd(self):
        return [str(self.output_binary), *self.run_args]

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
        dummy_c_file = self.source.with_suffix(".c")
        dummy_o_file = self.source.with_suffix(".o")
        self.logger.debug(f"Touching {dummy_c_file}")
        self.logger.debug(f"Touching {dummy_o_file}")
        dummy_c_file.touch()
        dummy_o_file.touch()
        return [
            "make",
            "-B",
            "-j",
            f"TARGET={self.output_binary.name}",
            f"SOURCE={self.source.with_suffix('').name}",
        ]


def main():
    app = SNbone(translator=Polly())
    print(f"{app.measure()=}")
    node = app.scops[0].schedule_tree[2]
    print(node.yaml_str)
    print(node.available_transformations)
    tr = node.available_transformations[0]
    print(tr)
    node.transform(tr)
    print(f"{app.legal=}")
    node = app.scops[0].schedule_tree[6]
    print(node.available_transformations)
    print(node.yaml_str)
    tr = node.available_transformations[1]
    print(tr)
    tile_size = 32, 32
    node.transform(tr, *tile_size)
    print(f"{app.legal=}")
    app.compile()
    tapp = app.generate_code(ephemeral=False)
    tapp.compile()
    print(f"{tapp.measure()=}")


if __name__ == "__main__":
    main()
    print("[DONE]")
