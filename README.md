# What is Sample Test Runner?

Sample Test Runner:

- scrapes sample inputs and outputs of coding contests on AtCoder and CodeForces - two of the major
  competitive programming platforms.
- runs sample tests against your solution and shows stats (only C++ is supported).

## Installation

Run the following commands in terminal.

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

###TODO
- check getchar dependency issue is resolved  by readchar. git+https://github.com/Cube707/python-readchar.git@v3.0.6 is out datated?
- only add PATH when it's not already done