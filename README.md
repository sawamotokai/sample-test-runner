# What is Sample Test Runner?

Sample Test Runner:

- scrapes sample inputs and outputs of coding contests on AtCoder and CodeForces - two of the major
  competitive programming platforms.
- runs sample tests against your solution and shows stats (only C++ is supported).

## Demo
- Parse contest
  ![Parsing contest](gifs/cpget-demo.gif)
- Run Sample Tests
  ![Run Sample Tests](gifs/cprun-demo.gif)

## Installation

Run the following commands in terminal.

u
```
sudo chmod +x install.sh
```

```
sudo ./install.sh
```

## How to use the program

### Fetching test cases

Run below command and follow the command line instructions.

```
cpget
```

### Testing your solution

- run the following in the workspace created (NOT inside a specific problem directory).

```
cprun <test case alphabet>
```

Example: `cprun c`
