
from dataclasses import dataclass
from drafter import *
from bakery import assert_equal


@dataclass
class Assignment:
    """Stores the information for one assignment."""
    name: str
    class_name: str
    due_date: str
    priority: str
    completed: bool  # True if the student has finished it


@dataclass
class State:
    """Keeps track of assignments and the selected filters."""
    assignments: list[Assignment]  # All assignments entered so far
    selected_class: str  # Which class to show, or "All"
    priority_filter: str  # Which priority to show, or "All"
    completed_count: int  # Number of finished assignments

def navigation() -> list:
    """Creates buttons for the five main pages.
    
    Parameters:
        None.
    
    Returns:
        A list of navigation buttons.
    
    Example:
        navigation() creates buttons for Home, Add Assignment, View Assignments, Progress Summary, and Settings.
    """
    return [
        Button("Home", "index"),
        Button("Add Assignment", "add_assignment"),
        Button("View Assignments", "view_assignments"),
        Button("Progress Summary", "summary"),
        Button("Settings", "settings")
    ]


def count_completed(assignments: list[Assignment]) -> int:
    """Counts how many assignments are finished.
    
    Parameters:
        assignments: A list of Assignment objects.
    
    Returns:
        The number of completed assignments as an integer.
    
    Example:
        count_completed(make_test_state().assignments) returns 1.
    """
    # Start at zero and add one for each finished assignment.
    total = 0

    for assignment in assignments:
        if assignment.completed:
            total = total + 1

    return total


def matches_filters(state: State, assignment: Assignment) -> bool:
    """Checks if an assignment matches both selected filters.
    
    Parameters:
        state: Stores the selected filters.
        assignment: The assignment being checked.
    
    Returns:
        True if the assignment matches both filters, otherwise False.
    
    Example:
        matches_filters(make_test_state(), make_test_state().assignments[0]) returns True.
    """
    # Both filters have to match before an assignment is shown.
    class_matches = False
    priority_matches = False

    if state.selected_class == "All":
        class_matches = True
    elif assignment.class_name == state.selected_class:
        class_matches = True

    if state.priority_filter == "All":
        priority_matches = True
    elif assignment.priority == state.priority_filter:
        priority_matches = True

    return class_matches and priority_matches


def get_classes(state: State) -> list[str]:
    """Makes a list of class names without duplicates.
    
    Parameters:
        state: Stores the assignments.
    
    Returns:
        A list of class names starting with "All".
    
    Example:
        get_classes(make_test_state()) returns ["All", "Math", "English"].
    """
    # "All" lets the student see assignments from every class.
    classes = ["All"]

    for assignment in state.assignments:
        if assignment.class_name not in classes:
            classes.append(assignment.class_name)

    return classes


def get_percentage(state: State) -> float:
    """Calculates the percentage of finished assignments.
    
    Parameters:
        state: Stores assignments and the completed count.
    
    Returns:
        The percentage completed, rounded to one decimal place.
    
    Example:
        get_percentage(make_test_state()) returns 50.0.
    """
    total = len(state.assignments)

    # Avoid dividing by zero when there are no assignments yet.
    if total == 0:
        return 0.0

    return round(state.completed_count / total * 100, 1)


@route
def index(state: State) -> Page:
    """Displays the home page and its navigation buttons.
    
    Parameters:
        state: Stores the current website information.
    
    Returns:
        A Page showing the home screen.
    
    Example:
        index(make_test_state()) creates the home page with the title "College Assignment Tracker".
    """
    return Page(state, [
        Header("College Assignment Tracker"),
        "Welcome to your assignment tracker!",
        "Keep your classes, deadlines, and assignments organized.",
        Header("Main Menu", 2),
        *navigation()
    ])


@route
def add_assignment(state: State) -> Page:
    """Displays the form for adding an assignment.
    
    Parameters:
        state: Stores the current website information.
    
    Returns:
        A Page with text boxes and a priority selection.
    
    Example:
        add_assignment(make_test_state()) creates a page with an assignment name text box.
    """
    return Page(state, [
        Header("Add a New Assignment"),
        "Assignment Name:",
        TextBox("name"),
        "Class Name:",
        TextBox("class_name"),
        "Due Date:",
        TextBox("due_date", placeholder="YYYY-MM-DD"),
        "Priority:",
        SelectBox("priority", ["High", "Medium", "Low"]),
        Button("Save Assignment", "save_assignment"),
        Header("Navigation", 3),
        *navigation()
    ])


@route
def save_assignment(state: State, name: str, class_name: str,
                    due_date: str, priority: str) -> Page:
    """Checks the form and saves a new unfinished assignment.
    
    Parameters:
        state: Stores the assignments.
        name: The assignment name.
        class_name: The class for the assignment.
        due_date: The date entered for the assignment.
        priority: The selected priority level.
    
    Returns:
        A Page confirming the assignment was saved, or showing missing information.
    
    Example:
        save_assignment(state, "Quiz", "Math", "2026-12-10", "High") adds a new Quiz assignment when state is valid.
    """
    # strip() removes extra spaces so a blank name does not count.
    if name.strip() == "" or class_name.strip() == "":
        return Page(state, [
            Header("Missing Information"),
            "Please enter an assignment name and class.",
            Button("Try Again", "add_assignment")
        ])

    if due_date.strip() == "":
        return Page(state, [
            Header("Missing Due Date"),
            "Please enter a due date.",
            Button("Try Again", "add_assignment")
        ])

    # A new assignment starts as unfinished.
    new_assignment = Assignment(
        name.strip(),
        class_name.strip(),
        due_date.strip(),
        priority,
        False
    )

    # Add the new Assignment object to the list in State.
    state.assignments.append(new_assignment)

    return Page(state, [
        Header("Assignment Saved!"),
        "Your assignment has been added successfully.",
        *navigation()
    ])


@route
def view_assignments(state: State) -> Page:
    """Displays assignments that match the chosen filters.
    
    Parameters:
        state: Stores assignments and the current filters.
    
    Returns:
        A Page listing matching assignments with their information and buttons.
    
    Example:
        view_assignments(make_test_state()) creates a page showing Homework 1 and Essay.
    """
    content = [
        Header("Your Assignments"),
        "Class Filter: " + state.selected_class,
        "Priority Filter: " + state.priority_filter,
        Button("Change Filters", "settings")
    ]

    # Count how many assignments are visible after filtering.
    shown = 0

    # Use each position in the list for the complete/delete buttons.
    for index_number in range(len(state.assignments)):
        assignment = state.assignments[index_number]

        if matches_filters(state, assignment):
            shown = shown + 1

            content.append(
                Header(assignment.name, 2)
            )
            content.append("Class: " + assignment.class_name)
            content.append("Due Date: " + assignment.due_date)
            content.append("Priority: " + assignment.priority)

            if assignment.completed:
                content.append("Status: Completed")
            else:
                content.append("Status: Not Completed")
                content.append(
                    Button(
                        "Mark Complete",
                        "complete_assignment",
                        [Argument("assignment_index", index_number)]
                    )
                )

            content.append(
                Button(
                    "Delete Assignment",
                    "delete_assignment",
                    [Argument("assignment_index", index_number)]
                )
            )

            content.append(HorizontalRule())

    if shown == 0:
        content.append("No assignments match your current filters.")

    # Put the navigation buttons at the bottom of the page.
    content.extend(navigation())

    return Page(state, content)


@route
def complete_assignment(state: State, assignment_index: int) -> Page:
    """Marks an assignment as finished and updates the count.
    
    Parameters:
        state: Stores assignments and the completed count.
        assignment_index: The position of the assignment in the list.
    
    Returns:
        A Page showing the updated assignment list.
    
    Example:
        complete_assignment(state, 0) marks the first assignment complete if it exists.
    """
    if 0 <= assignment_index < len(state.assignments):
        assignment = state.assignments[assignment_index]

        # Only count it once, even if the button is used again.
        if not assignment.completed:
            assignment.completed = True
            state.completed_count = state.completed_count + 1

    return view_assignments(state)


@route
def delete_assignment(state: State, assignment_index: int) -> Page:
    """Deletes an assignment and adjusts the completed count if needed.
    
    Parameters:
        state: Stores assignments and the completed count.
        assignment_index: The position of the assignment to delete.
    
    Returns:
        A Page showing the updated assignment list.
    
    Example:
        delete_assignment(state, 0) removes the first assignment if it exists.
    """
    if 0 <= assignment_index < len(state.assignments):
        assignment = state.assignments[assignment_index]

        # If it was finished, remove it from the completed total too.
        if assignment.completed:
            state.completed_count = state.completed_count - 1

        state.assignments.pop(assignment_index)

    return view_assignments(state)


@route
def summary(state: State) -> Page:
    """Shows totals and the percentage of completed assignments.
    
    Parameters:
        state: Stores assignments and the completed count.
    
    Returns:
        A Page showing the progress summary.
    
    Example:
        summary(make_test_state()) creates a page showing 2 total assignments and 50.0% completed.
    """
    total = len(state.assignments)
    completed = state.completed_count
    # Unfinished assignments are everything not marked complete.
    unfinished = total - completed
    percentage = get_percentage(state)

    return Page(state, [
        Header("Progress Summary"),
        "Total Assignments: " + str(total),
        "Completed Assignments: " + str(completed),
        "Unfinished Assignments: " + str(unfinished),
        "Percentage Completed: " + str(percentage) + "%",
        *navigation()
    ])


@route
def settings(state: State) -> Page:
    """Displays the class and priority filter choices.
    
    Parameters:
        state: Stores assignments and selected filters.
    
    Returns:
        A Page where the user can choose filters.
    
    Example:
        settings(make_test_state()) creates a page with class and priority dropdowns.
    """
    classes = get_classes(state)

    # A deleted class may no longer be an available option.
    if state.selected_class not in classes:
        state.selected_class = "All"

    return Page(state, [
        Header("Settings"),
        "Choose which assignments you want to see.",
        "Filter by Class:",
        SelectBox("selected_class", classes, state.selected_class),
        "Filter by Priority:",
        SelectBox(
            "priority_filter",
            ["All", "High", "Medium", "Low"],
            state.priority_filter
        ),
        Button("Apply Filters", "update_filters"),
        Header("Navigation", 3),
        *navigation()
    ])


@route
def update_filters(state: State, selected_class: str,
                   priority_filter: str) -> Page:
    """Saves the selected filters and displays matching assignments.
    
    Parameters:
        state: Stores assignments and selected filters.
        selected_class: The class to show, or "All".
        priority_filter: The priority to show, or "All".
    
    Returns:
        A Page showing assignments with the updated filters.
    
    Example:
        update_filters(state, "Math", "High") sets the filters to Math and High.
    """
    # Save these choices in State so other pages can use them.
    state.selected_class = selected_class
    state.priority_filter = priority_filter

    return view_assignments(state)


def make_test_state() -> State:
    """Creates sample assignments for testing the website.
    
    Parameters:
        None.
    
    Returns:
        A State with two assignments, one already completed.
    
    Example:
        make_test_state() returns a State with Homework 1 and Essay and a completed count of 1.
    """
    # One finished and one unfinished assignment for testing.
    return State([
        Assignment("Homework 1", "Math", "2026-12-01", "High", False),
        Assignment("Essay", "English", "2026-12-05", "Low", True)
    ], "All", "All", 1)


# Check the smaller functions before testing the website pages.
test_state = make_test_state()

assert_equal(count_completed(test_state.assignments), 1)
assert_equal(get_percentage(test_state), 50.0)
assert_equal(get_classes(test_state), ["All", "Math", "English"])
assert_equal(matches_filters(test_state, test_state.assignments[0]), True)


# Make sure each main page contains something we expect to see.
assert_has(index(make_test_state()), Header("College Assignment Tracker"))
assert_has(add_assignment(make_test_state()), TextBox("name"))
assert_has(view_assignments(make_test_state()), Header("Your Assignments"))
assert_has(summary(make_test_state()), Header("Progress Summary"))
assert_has(settings(make_test_state()), Header("Settings"))


# Make sure saving adds a new assignment to the list.
test_state = State([], "All", "All", 0)

save_assignment(test_state, "Quiz", "Math", "2026-12-10", "High")

assert_equal(len(test_state.assignments), 1)
assert_equal(test_state.assignments[0].name, "Quiz")
assert_equal(test_state.completed_count, 0)


# An empty name should not create an assignment.
test_state = State([], "All", "All", 0)

save_assignment(test_state, "", "Math", "2026-12-10", "High")

assert_equal(len(test_state.assignments), 0)


# Completing an assignment should update both its status and the count.
test_state = make_test_state()

complete_assignment(test_state, 0)

assert_equal(test_state.assignments[0].completed, True)
assert_equal(test_state.completed_count, 2)


# Clicking complete twice should not count the same assignment twice.
complete_assignment(test_state, 0)

assert_equal(test_state.completed_count, 2)


# Deleting a finished assignment should lower the completed count.
test_state = make_test_state()

delete_assignment(test_state, 1)

assert_equal(len(test_state.assignments), 1)
assert_equal(test_state.completed_count, 0)


# Deleting unfinished work should leave the completed count alone.
test_state = make_test_state()

delete_assignment(test_state, 0)

assert_equal(len(test_state.assignments), 1)
assert_equal(test_state.completed_count, 1)


# Changing filters should update State and affect which assignments match.
test_state = make_test_state()

update_filters(test_state, "Math", "High")

assert_equal(test_state.selected_class, "Math")
assert_equal(test_state.priority_filter, "High")
assert_equal(matches_filters(test_state, test_state.assignments[0]), True)
assert_equal(matches_filters(test_state, test_state.assignments[1]), False)



set_website_title("College Assignment Tracker")

set_site_information(
    "Kira Novosel",
    "A website for organizing college assignments and tracking progress.",
    "Drafter documentation and AI assistance",
    "See the planning document in the GitHub repository.",
    []
)


start_server(State([], "All", "All", 0))
