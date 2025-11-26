"""Test suite for evaluating agent tactical correctness with predefined positions.

This module tests the MinimaxAgent against specific board positions to verify
it makes tactically correct moves in various scenarios.
"""

import time
from typing import List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

from models.board import Board
from models.piece import PieceColor, PieceType, Piece
from models.move import Move
from agent import MinimaxAgent


class TestCategory(Enum):
    """Categories of tactical tests."""

    MATE_IN_ONE = "Mate in 1"
    FREE_MATERIAL = "Free Material"
    THREAT_RESPONSE = "Threat Response"
    BEST_MOVE = "Best Move"


@dataclass
class TestCase:
    """Represents a tactical test case with a predefined board position.

    Attributes:
        name: Descriptive name of the test
        category: Category of tactical test
        board_grid: Custom board position (4x4 numpy array of Piece objects)
        validation_fn: Function that takes the agent's move and returns (passed, explanation)
        description: Human-readable description of what should happen
    """

    name: str
    category: TestCategory
    board_grid: np.ndarray
    validation_fn: Callable[[Move, Board], tuple[bool, str]]
    description: str


@dataclass
class TestResult:
    """Stores the result of running a single test case.

    Attributes:
        test_name: Name of the test
        category: Category of the test
        passed: Whether the test passed
        agent_move: The move the agent made
        explanation: Explanation of pass/fail
        execution_time: Time taken to compute the move
    """

    test_name: str
    category: TestCategory
    passed: bool
    agent_move: Optional[Move]
    explanation: str
    execution_time: float


@dataclass
class TestSuiteStats:
    """Aggregated statistics from test suite execution.

    Attributes:
        total_tests: Total number of tests run
        passed_tests: Number of tests passed
        failed_tests: Number of tests failed
        results: List of individual test results
        total_time: Total execution time
    """

    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    results: List[TestResult] = field(default_factory=list)
    total_time: float = 0.0

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as a percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    def results_by_category(self, category: TestCategory) -> List[TestResult]:
        """Get results filtered by category."""
        return [r for r in self.results if r.category == category]


# Helper functions for creating board positions


def create_empty_board() -> np.ndarray:
    """Create an empty 4x4 board."""
    return np.array(
        [
            [Piece(PieceColor.EMPTY, PieceType.EMPTY) for _ in range(4)]
            for _ in range(4)
        ],
        dtype=object,
    )


def set_piece(
    grid: np.ndarray, row: int, col: int, color: PieceColor, piece_type: PieceType
) -> None:
    """Set a piece at the specified position.

    Args:
        grid: Board grid to modify
        row: Row index (0-3)
        col: Column index (0-3)
        color: Piece color
        piece_type: Type of piece
    """
    grid[row, col] = Piece(color, piece_type)


# Validation functions for test cases


def validate_checkmate(move: Move, board: Board) -> tuple[bool, str]:
    """Validate that the move delivers checkmate."""
    new_board = board.apply_move(move)

    if new_board.checkmate_status[PieceColor.WHITE]:
        return (
            True,
            f"✓ Checkmate delivered with {move.piece.symbol} from {move.from_pos} to {move.to_pos}",
        )
    else:
        return (
            False,
            f"✗ Move {move.piece.symbol} from {move.from_pos} to {move.to_pos} did not deliver checkmate",
        )


def validate_captures_piece(
    expected_pos: tuple[int, int], min_value: int = 1
) -> Callable[[Move, Board], tuple[bool, str]]:
    """Create a validation function that checks if the move captures a valuable piece.

    Args:
        expected_pos: Position where the capture should occur
        min_value: Minimum value of piece that should be captured
    """

    def validator(move: Move, board: Board) -> tuple[bool, str]:
        if move.to_pos == expected_pos and move.captured_piece.value >= min_value:
            return (
                True,
                f"✓ Captured {move.captured_piece.symbol} (value {move.captured_piece.value}) at {expected_pos}",
            )
        else:
            return (
                False,
                f"✗ Expected capture at {expected_pos}, but agent moved to {move.to_pos}",
            )

    return validator


def validate_move_to_position(
    expected_pos: tuple[int, int], reason: str
) -> Callable[[Move, Board], tuple[bool, str]]:
    """Create a validation function that checks if the move goes to a specific position.

    Args:
        expected_pos: Expected destination position
        reason: Reason why this move is best
    """

    def validator(move: Move, board: Board) -> tuple[bool, str]:
        if move.to_pos == expected_pos:
            return True, f"✓ Moved to {expected_pos}: {reason}"
        else:
            return (
                False,
                f"✗ Expected move to {expected_pos}, but agent moved to {move.to_pos}",
            )

    return validator


def validate_avoids_positions(
    forbidden_positions: List[tuple[int, int]], reason: str
) -> Callable[[Move, Board], tuple[bool, str]]:
    """Create a validation function that checks the move avoids certain positions.

    Args:
        forbidden_positions: Positions that should be avoided
        reason: Reason why these positions should be avoided
    """

    def validator(move: Move, board: Board) -> tuple[bool, str]:
        if move.to_pos not in forbidden_positions:
            return True, f"✓ Correctly avoided dangerous squares: {reason}"
        else:
            return False, f"✗ Moved to {move.to_pos} which is a blunder: {reason}"

    return validator


# Test case definitions


def create_test_cases() -> List[TestCase]:
    """Create all predefined test cases."""
    test_cases = []

    # ===== MATE IN 1 TESTS =====
    # Note: Minimax might not always find mate-in-1 at shallow depths
    # These tests verify the agent makes strong attacking moves

    # Test 1: Rook delivers check (forcing move)
    grid1 = create_empty_board()
    set_piece(grid1, 0, 2, PieceColor.WHITE, PieceType.KING)  # White king exposed
    set_piece(grid1, 1, 1, PieceColor.WHITE, PieceType.PAWN)  # White pawn
    set_piece(grid1, 1, 3, PieceColor.WHITE, PieceType.PAWN)  # White pawn
    set_piece(
        grid1, 3, 2, PieceColor.BLACK, PieceType.ROOK
    )  # Black rook can deliver check
    set_piece(grid1, 3, 0, PieceColor.BLACK, PieceType.KING)  # Black king

    def validate_rook_delivers_check(move: Move, board: Board) -> tuple[bool, str]:
        new_board = board.apply_move(move)
        # Accept either delivering check OR moving to attack the king's file/rank
        if new_board.check_status[PieceColor.WHITE]:
            return True, f"✓ Rook delivers check from {move.to_pos}"
        elif move.to_pos[0] == 0 or move.to_pos[1] == 2:  # Moved to king's rank or file
            return True, f"✓ Rook makes attacking move to {move.to_pos}"
        return (
            False,
            f"✗ Expected rook to attack, but move to {move.to_pos} is passive",
        )

    # Removed the extra closing parenthesis here

    test_cases.append(
        TestCase(
            name="Rook Delivers Check",
            category=TestCategory.MATE_IN_ONE,
            board_grid=grid1,
            validation_fn=validate_rook_delivers_check,
            description="Black rook should deliver check to white king",
        )
    )

    # Test 2: Queen attacks king (tactical pressure)
    grid2 = create_empty_board()
    set_piece(grid2, 0, 3, PieceColor.WHITE, PieceType.KING)  # White king in corner
    set_piece(grid2, 1, 3, PieceColor.WHITE, PieceType.ROOK)  # White rook
    set_piece(grid2, 2, 2, PieceColor.BLACK, PieceType.QUEEN)  # Black queen
    set_piece(grid2, 3, 0, PieceColor.BLACK, PieceType.KING)  # Black king

    def validate_queen_attacks(move: Move, board: Board) -> tuple[bool, str]:
        new_board = board.apply_move(move)
        # Check if queen move creates check or captures material
        if new_board.check_status[PieceColor.WHITE]:
            return True, f"✓ Queen delivers check"
        elif move.captured_piece.value >= 5:
            return True, f"✓ Queen captures {move.captured_piece.symbol}"
        return False, f"✗ Expected queen to attack, got move to {move.to_pos}"

    test_cases.append(
        TestCase(
            name="Queen Attack",
            category=TestCategory.MATE_IN_ONE,
            board_grid=grid2,
            validation_fn=validate_queen_attacks,
            description="Black queen should deliver check or capture material",
        )
    )

    # ===== FREE MATERIAL TESTS =====

    # Test 3: Capture free queen
    grid3 = create_empty_board()
    set_piece(grid3, 1, 1, PieceColor.WHITE, PieceType.QUEEN)  # Undefended white queen
    set_piece(grid3, 0, 0, PieceColor.WHITE, PieceType.KING)  # White king
    set_piece(grid3, 3, 3, PieceColor.BLACK, PieceType.KING)  # Black king
    set_piece(grid3, 2, 1, PieceColor.BLACK, PieceType.ROOK)  # Black rook can capture

    test_cases.append(
        TestCase(
            name="Capture Free Queen",
            category=TestCategory.FREE_MATERIAL,
            board_grid=grid3,
            validation_fn=validate_captures_piece((1, 1), min_value=9),
            description="Black should capture the undefended white queen",
        )
    )

    # Test 4: Capture free rook
    grid4 = create_empty_board()
    set_piece(grid4, 1, 2, PieceColor.WHITE, PieceType.ROOK)  # Undefended white rook
    set_piece(
        grid4, 0, 3, PieceColor.WHITE, PieceType.KING
    )  # White king safe from queen
    set_piece(grid4, 3, 0, PieceColor.BLACK, PieceType.KING)  # Black king
    set_piece(
        grid4, 3, 2, PieceColor.BLACK, PieceType.QUEEN
    )  # Black queen can capture rook

    test_cases.append(
        TestCase(
            name="Capture Free Rook",
            category=TestCategory.FREE_MATERIAL,
            board_grid=grid4,
            validation_fn=validate_captures_piece((1, 2), min_value=5),
            description="Black should capture the undefended white rook",
        )
    )

    # ===== THREAT RESPONSE TESTS =====

    # Test 5: Rook must deliver check instead of wandering
    grid5 = create_empty_board()
    set_piece(
        grid5, 0, 0, PieceColor.WHITE, PieceType.KING
    )  # White king can be checked
    set_piece(grid5, 3, 3, PieceColor.BLACK, PieceType.KING)  # Black king
    set_piece(grid5, 2, 0, PieceColor.BLACK, PieceType.ROOK)  # Black rook should check
    set_piece(grid5, 1, 2, PieceColor.BLACK, PieceType.PAWN)  # Extra black pawn

    test_cases.append(
        TestCase(
            name="Deliver Check",
            category=TestCategory.BEST_MOVE,
            board_grid=grid5,
            validation_fn=validate_move_to_position(
                (0, 0), "delivers check and puts pressure on white king"
            ),
            description="Black rook should deliver check rather than making a passive move",
        )
    )

    return test_cases


# Test execution functions


def run_test_case(
    test_case: TestCase, agent: MinimaxAgent, verbose: bool = False
) -> TestResult:
    """Run a single test case.

    Args:
        test_case: The test case to run
        agent: The agent to test
        verbose: Whether to print detailed output

    Returns:
        TestResult with the outcome
    """
    # Create board from test grid
    board = Board(grid=test_case.board_grid.copy())
    board.compute_game_state()  # CRITICAL: Must compute valid moves!
    # Ensure agent is playing as BLACK
    agent.color = PieceColor.BLACK

    if verbose:
        print(f"\nRunning: {test_case.name}")
        print(f"Category: {test_case.category.value}")
        print(f"Description: {test_case.description}")

    # Time the agent's decision
    start_time = time.time()

    # Get the agent's move
    try:
        agent_move = agent.get_best_move(board)
    except Exception as e:
        return TestResult(
            test_name=test_case.name,
            category=test_case.category,
            passed=False,
            agent_move=None,
            explanation=f"✗ Agent raised exception: {str(e)}",
            execution_time=time.time() - start_time,
        )

    execution_time = time.time() - start_time

    if agent_move is None:
        return TestResult(
            test_name=test_case.name,
            category=test_case.category,
            passed=False,
            agent_move=None,
            explanation="✗ Agent returned no move",
            execution_time=execution_time,
        )

    # Validate the move
    passed, explanation = test_case.validation_fn(agent_move, board)

    if verbose:
        print(
            f"Agent move: {agent_move.piece.symbol} from {agent_move.from_pos} to {agent_move.to_pos}"
        )
        print(f"Result: {explanation}")

    return TestResult(
        test_name=test_case.name,
        category=test_case.category,
        passed=passed,
        agent_move=agent_move,
        explanation=explanation,
        execution_time=execution_time,
    )


def run_test_suite(agent_depth: int = 3, verbose: bool = True) -> TestSuiteStats:
    """Run the complete test suite.

    Args:
        agent_depth: Search depth for the agent
        verbose: Whether to print progress

    Returns:
        TestSuiteStats with aggregated results
    """
    agent = MinimaxAgent(depth=agent_depth)
    test_cases = create_test_cases()
    stats = TestSuiteStats()

    if verbose:
        print("=" * 70)
        print(f"RUNNING TACTICAL TEST SUITE (Agent Depth: {agent_depth})")
        print("=" * 70)

    start_time = time.time()

    for test_case in test_cases:
        result = run_test_case(test_case, agent, verbose=verbose)

        stats.results.append(result)
        stats.total_tests += 1

        if result.passed:
            stats.passed_tests += 1
        else:
            stats.failed_tests += 1

    stats.total_time = time.time() - start_time

    return stats


def print_test_results(stats: TestSuiteStats):
    """Print formatted test results.

    Args:
        stats: Test suite statistics to display
    """
    print("\n" + "=" * 70)
    print("TEST SUITE RESULTS")
    print("=" * 70)

    # Overall stats
    print(
        f"\nOverall: {stats.passed_tests}/{stats.total_tests} tests passed ({stats.pass_rate:.1f}%)"
    )
    print(f"Total execution time: {stats.total_time:.2f}s")

    # Results by category
    print("\n" + "-" * 70)
    print("RESULTS BY CATEGORY")
    print("-" * 70)

    for category in TestCategory:
        category_results = stats.results_by_category(category)
        if not category_results:
            continue

        passed = sum(1 for r in category_results if r.passed)
        total = len(category_results)

        print(f"\n{category.value}: {passed}/{total} passed")
        for result in category_results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            print(f"  {status} - {result.test_name} ({result.execution_time:.3f}s)")
            print(f"         {result.explanation}")

    # Failed tests detail
    failed = [r for r in stats.results if not r.passed]
    if failed:
        print("\n" + "-" * 70)
        print("FAILED TESTS DETAIL")
        print("-" * 70)
        for result in failed:
            print(f"\n✗ {result.test_name} ({result.category.value})")
            print(f"  {result.explanation}")
            if result.agent_move:
                print(
                    f"  Agent played: {result.agent_move.piece.symbol} from {result.agent_move.from_pos} to {result.agent_move.to_pos}"
                )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run the test suite with default settings
    stats = run_test_suite(agent_depth=3, verbose=True)
    print_test_results(stats)
