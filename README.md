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

```
sudo chmod +x install.sh
```

```
sudo ./install.sh
```
#### If you want to use this program, you have to set the following environment variables for the program to be authenticated by the contest website.
```
export ATCODER_USERNAME=<your username>
export ATCODER_PASSWORD=<your password>
export CODEFORCES_USERNAME=<your username>
export CODEFORCES_PASSWORD=<your password>
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
