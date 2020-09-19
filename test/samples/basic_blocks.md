# Line endings are important not only in Markdown...

## Soft break

Line
continues - this is "soft break".

## Hard break

Line.  
Another Line because the previous ends with at least two spaces.

Line.\
Another line because the previous ends with a "\\".

## Other block elements

Column A | Column B | Column C
---------|----------|---------
 A1 | B1 | C1
 A2 | B2 | C2
 A3 | B3 | C3

A paragraph under a table.

----
A paragraph under a horizontal line.

## Code blocks

Java code:

```java
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello World!");
    }
}
```

Log file:

    2020-07-05 10:20:55 ...
    2020-07-05 10:20:56 ...
        ...
    2020-07-05 10:21:03 ...
