# RISC CPU Implementation

## Hardware Design

In this project, we implemented a 16-bit RISC CPU by using VHDL. It is a very simple CPU that has no pipeline architecture. It basically has ALU, Register File, Instruction Register and Control Unit. Since there is no pipeline, we did not implement pipeline related logics like pipeline hazard unit, pipeline registers, etc. 
Implemented Architecture (Some enhancement has been done on that drawing):
![Architecture](https://github.com/kaanari/RISC-V/blob/main/assets/architecture.png)

## Software Support

In addition, we also created assembler and emulator for the provided CPU. They are programmed in Python 3. By using these tools, one can easily debug their code for RISC CPU or see expected results without programming CPU.
We provide jump instructions with labels in the development tool. By this feature, software developers do not need to calculate and insert all the memory offsets manually to implement loops and jumps. Instead, they can just write codes with human readible strings and let the compiler do the dirty works.

Emulator offers some fundamental debbugger features like Step Into, Step Back, Run, Stop.

![Emulator](https://github.com/kaanari/RISC-V/blob/main/assets/emulator.gif)

## Future works

We may improve the architecture like adding pipeline, increasing instructions, optimizing the hardware implementation. In the assembler and emulator side, we may update it with respect to architecture enhancements. 

## Built With

* VHDL 
* [Intel Quartus Prime](https://www.intel.com/content/www/us/en/software/programmable/quartus-prime/overview.html) 
* [Python 3](https://www.python.org/) 

## Authors

* 👤**Kaan ARI**  - [kaanari](https://github.com/kaanari)
* 👤**Ayşe İDMAN**  - [ayseidman](https://github.com/ayseidman)

See also the list of [contributors](https://github.com/kaanari/RISC-V/graphs/contributors) who are participated in this project.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](https://github.com/kaanaritr/Coursera-GDrive/blob/master/LICENSE) file for details.
