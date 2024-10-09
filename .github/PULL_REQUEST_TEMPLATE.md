# Pull Request Template

## Description

Please include a summary of the changes and the related issue. Provide relevant motivation and context.

## How Has This Been Tested?

Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce. Include any relevant details for your test configuration.

- **Test Cases:**
  - [ ] Unit tests
  - [ ] Integration tests
  - [ ] Manual tests
  - [ ] No tests required

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist

- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Reviewer Checklist

- [ ] Checked the PR description and adherence to the template
- [ ] Verified that logging standards are met
- [ ] Ensured coding standards are followed
- [ ] Confirmed design best practices are implemented
- [ ] Reviewed test coverage and results
- [ ] Approved changes or provided constructive feedback

## Best Practices

### Logging

- [ ] **Critical Events Logged**: Verify that all critical operations, errors, and exceptions are logged.
- [ ] **No PII Logged**: Ensure no PII or sensitive data is logged.
- [ ] **5 W's Included**: Check that log entries include what, when, where, who, and why/how.
- [ ] **Correct Log Levels**: Confirm that log levels are used appropriately.
- [ ] **Unique Identifiers**: Ensure log messages have unique identifiers for tracing.
- [ ] **Consistent Formatting**: Verify that log message formatting is consistent.
- [ ] **Descriptive Logs**: Ensure log messages are clear, detailed, and avoid magic numbers.
- [ ] **Operational Metrics**: Check that performance and monitoring logs are present.
- [ ] **Security Best Practices**: Ensure logs are anonymized if necessary and stored securely.
- [ ] **Updated Documentation**: Confirm that logging practices are documented and up-to-date.
- [ ] **Common Mistakes Avoided**: Check for missing timestamps, vague descriptions, and lack of source/destination info.
- [ ] **Target Audience Consideration**: Ensure logs are written appropriately for their intended audience (customers, internal devs, alert systems).
- [ ] **When/Where Not to Log**: Verify that logging is not excessive, does not occur in performance-sensitive areas, avoids redundancy, and does not include temporary data.
- [ ] **Actionable Urgent Logs**: Ensure urgent logs provide clear follow-up actions, such as links to documentation, next steps, or contact information.

### Design Patterns & Implementation

- **Design Pattern Reference**: Refer to the Design Pattern CheatSheet by Itchimonji on CP Massive Programming.
- **Class Cohesion**: Ensure each class represents one abstract data type. Split or hide functions if mixed.
- **Complementary Functions**: When creating a function, consider if a complementary function is required (e.g., turning on/off light).

#### Interface Design

- **Programmatic Interfaces**: Make interfaces programmatic rather than semantic.
- **Data Exposure**: Avoid exposing data/functions at accessible levels where not needed. Use getters/setters for member variables.
- **Adherence to Contract**: Design and implement classes to adhere to the contract implied by the class interface.
- **Interface Details**: Do not use interfaces that depend on implicit/internal implementation details.

#### Class and Routine Design

- **Data Members**: Be critical of classes with more than about seven data members.
- **Base Classes**: Be suspicious of base classes with only one derived class.
- **Routine Override**: Be suspicious of classes that override a routine and do nothing. Consider changing to HasA.
- **Routine Count**: Keep the number of routines in a class as small as possible.
- **Routine Calls**: Minimize the number of different routines called by a class.
- **Law of Demeter**: Only interact with immediate friends.

#### Initialization and Copying

- **Member Data Initialization**: Initialize all member data in all constructors if possible.
- **Deep Copy**: Prefer deep copy over shallow copy unless performance is significantly worse.

#### Class Design

- **God Class**: Avoid God Class.
- **Irrelevant Classes**: Eliminate irrelevant classes that only contain data.

#### Functional Cohesion

- **Function Cohesion**: Functions should perform what their name suggests.
- **Temporal Cohesion**: Avoid combining operations into a routine just because they occur at the same time. Extract sub-routines.
- **Coincidental Cohesion**: Redesign routines with no discernible relationship between operations.

#### Naming Conventions

- **Routine Names**: Make names of routines as long as necessary.
- **Parameter Order**: Put parameters in input-modify-output order.
- **Parameter Count**: Limit the number of routine parameters to about seven.

#### Error Handling

- **Error Handling Code**: Use for expected conditions; use assertions for conditions that should never occur.
- **Graceful Error Response**: Ensure error-handling code enables graceful responses. Use assertions for code changes.
- **Local Error Handling**: Handle errors locally if possible.
- **Constructor/Destructor Exceptions**: Avoid throwing exceptions in constructors and destructors unless caught in the same place.
- **Empty Catch Blocks**: Avoid them.
- **Exception Abstraction**: Ensure exceptions passed to the caller are consistent with the routine interface's abstraction.

#### Data Safety

- **Public Method Responsibility**: Public methods should sanitize data. Private methods can assume the data is safe after this.
- **Public Function Barricades**: Handle unreliable data and use error handling in public functions. Use assertions for data passed these functions.

#### Code Cleanliness

- **Trivial Error Checks**: Remove code that checks for trivial errors.
- **Crash Handling**: Remove code that results in hard crashes unless mission-critical. Leave code that helps the program crash gracefully.
- **Variable Initialization**: Initialize variables as declared or as close as possible.
- **Variable Lifespan**: Keep variables alive for as short a time as possible.
- **Variable Purpose**: Use variables for exactly one purpose and avoid hidden meanings.
- **Variable Naming**: Put the modifier at the end (e.g., RevenueAverage). Avoid names with similar meanings and variables with different meanings but similar names.
- **Global Variables**: Identify and define a common prefix qualifier for global variables for easy recognition.

#### Error Prevention

- **Divide-by-Zero Errors**: Anticipate and handle them.
- **Type Conversions**: Make them obvious.
- **Mixed-Type Comparisons**: Avoid them.

#### Enumerated Types

- **Invalid Entry**: Reserve the first entry in the enumerated type as invalid.

#### Routine Naming and Dependencies

- **Routine Dependencies**: Name routines so dependencies are obvious. Document unclear dependencies with comments.
- **Code Readability**: Make code read from top to bottom. Group related statements.
- **Loop Index**: Don’t manipulate the loop index to terminate a loop.
- **Loop Design**: Keep loops short and limit nesting to three levels.
- **Guard Clauses**: Use them for early returns or exits to simplify complex error processing.
- **Nested Conditions**: Simplify nested if statements by retesting parts of the condition or factoring deeply nested code into its own routine.
