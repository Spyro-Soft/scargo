#!/usr/bin/env python3
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List
from xml.etree import ElementTree

import matplotlib.pyplot as plt
import typer
from matplotlib.axes import Axes
from matplotlib.patches import Circle
from matplotlib.ticker import FormatStrFormatter


@dataclass
class TestCase:
    classname: str
    name: str
    time: float

    @classmethod
    def from_element(cls, element: ElementTree.Element) -> "TestCase":
        return cls(
            element.attrib["classname"],
            element.attrib["name"],
            float(element.attrib["time"]),
        )


@dataclass
class TestData:
    tests: int
    failures: int
    errors: int
    skipped: int
    total_duration_ms: int
    test_cases: List[TestCase]

    @property
    def passed(self) -> int:
        return self.tests - self.failures - self.errors - self.skipped

    @property
    def test_case_durations_ms(self) -> List[float]:
        return [int(test_case.time * 1000) for test_case in self.test_cases]


@dataclass
class CoverageData:
    line_coverage: float
    branch_coverage: float


def app(
    junitxml_path: Path = typer.Argument(..., exists=True, dir_okay=False),
    cobertura_path: Path = typer.Argument(..., exists=True, dir_okay=False),
    output_pdf: Path = typer.Argument(..., dir_okay=False),
    test_type: str = typer.Option("", "-t", "--type"),
) -> None:
    test_data = parse_junitxml(junitxml_path)
    coverage_data = parse_cobertura(cobertura_path)
    plt.rcParams.update({"font.size": 7})
    fig, axs = plt.subplots(2, 2, width_ratios=(1, 2))
    fig.suptitle(f"Scargo {test_type.title()} Test Report {date.today().isoformat()}")
    add_test_info(axs[0, 0], test_data)
    add_test_pie_chart(axs[0, 1], test_data)
    add_coverage_info(axs[1, 0], coverage_data)
    add_test_duration_histogram(axs[1, 1], test_data)
    plt.savefig(output_pdf)


def parse_junitxml(junitxml_path: Path) -> TestData:
    tree = ElementTree.parse(junitxml_path)
    root = tree.getroot()
    tests = sum(int(suite.attrib["tests"]) for suite in root)
    failures = sum(int(suite.attrib["failures"]) for suite in root)
    errors = sum(int(suite.attrib["errors"]) for suite in root)
    skipped = sum(int(suite.attrib["skipped"]) for suite in root)
    total_time = sum(float(suite.attrib["time"]) for suite in root)
    total_time_ms = int(total_time * 1000)
    test_cases = [TestCase.from_element(testcase) for suite in root for testcase in suite]
    return TestData(tests, failures, errors, skipped, total_time_ms, test_cases)


def parse_cobertura(cubertura_path: Path) -> CoverageData:
    tree = ElementTree.parse(cubertura_path)
    root = tree.getroot()
    return CoverageData(float(root.attrib["line-rate"]), float(root.attrib["branch-rate"]))


def add_test_info(ax: Axes, test_data: TestData) -> None:  # type: ignore[no-any-unimported]
    ax.set_axis_off()
    ax.text(0, 0.6, f"{test_data.tests} test cases", fontsize=20)
    ax.text(0, 0.2, f"Total duration: {test_data.total_duration_ms} ms", fontsize=13)


def add_test_pie_chart(ax: Axes, test_data: TestData) -> None:  # type: ignore[no-any-unimported]
    ax.set_title("Test Case Status")
    marks = [test_data.passed, test_data.failures, test_data.errors, test_data.skipped]
    colors = ["green", "red", "yellow", "grey"]
    patches, *_ = ax.pie(marks, colors=colors)
    white_circle = Circle((0, 0), 0.7, color="white")
    ax.add_artist(white_circle)
    labels = ["passed", "failed", "errors", "skipped"]
    percents = [f"{mark / test_data.tests * 100:.0f}% {label}" for label, mark in zip(labels, marks)]
    ax.legend(patches, percents, prop={"size": 7}, bbox_to_anchor=(0.9, 1))
    Circle((0, 0), 0.7, color="white")


def add_coverage_info(ax: Axes, coverage_data: CoverageData) -> None:  # type: ignore[no-any-unimported]
    ax.set_axis_off()
    fontsize = 9
    ax.text(0, 0.8, "Line coverage:", fontsize=fontsize)
    ax.text(0.75, 0.8, f"{coverage_data.line_coverage * 100:.1f}%", fontsize=fontsize)
    ax.text(0, 0.65, "Branch coverage:", fontsize=fontsize)
    ax.text(0.75, 0.65, f"{coverage_data.branch_coverage * 100:.1f}%", fontsize=fontsize)


def add_test_duration_histogram(ax: Axes, test_data: TestData) -> None:  # type: ignore[no-any-unimported]
    ax.set_title("Test Case Durations")
    ax.hist(test_data.test_case_durations_ms)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_formatter(FormatStrFormatter("%d ms"))


if __name__ == "__main__":
    typer.run(app)
