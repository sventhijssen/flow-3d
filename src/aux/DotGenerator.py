import subprocess


class DotGenerator:

    @staticmethod
    def generate(benchmark_name: str, content: str):
        dot_file_name = benchmark_name + ".dot"
        png_file_name = benchmark_name + ".png"
        with open(dot_file_name, 'w') as f:
            f.write(content)
        subprocess.call(["dot", "-Tpng", dot_file_name, "-o", png_file_name], stdout=subprocess.DEVNULL)
