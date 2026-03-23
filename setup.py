from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="servicios_publicos",
    version="1.0.0",
    author="Servicios Públicos Colombia",
    description="Aplicación ERPNext para gestión de servicios públicos en Colombia",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "frappe-bench >= 5.0",
    ],
)
