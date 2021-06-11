library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use work.CPU_library.all;

entity CPU is

	generic(
				DATA_WIDTH 		: integer := 16				
	);
	
	port(
			instruction	: in std_logic_vector((DATA_WIDTH-1) downto 0);
			CLK			: in std_logic;
			Reset 		: in std_logic;
			Mem_write	: out std_logic;
			Mem_read		: out std_logic;
			i_address	: out std_logic_vector((DATA_WIDTH-1) downto 0);
			i_data		: out std_logic_vector((DATA_WIDTH-1) downto 0);
			Cu_state		: out std_logic_vector(3 downto 0);
			flags			: out std_logic_vector(4 downto 0)		
	);

end CPU;

architecture structural of CPU is
	signal IR_write	: std_logic;
	signal OpCode 		: std_logic_vector(3 downto 0);
	signal Rd			: std_logic_vector(3 downto 0);
	signal Rs1			: std_logic_vector(3 downto 0);
	signal Rs2			: std_logic_vector(3 downto 0);
	signal Immediate	: std_logic_vector(7 downto 0);
	
	signal Rs2_select : std_logic;
	signal GPReg_Rs2	: std_logic_vector(3 downto 0);
	
	signal GPRF_wr  	: std_logic;
	signal data_in  	: std_logic_vector((DATA_WIDTH-1) downto 0);
	signal data_Rs1 	: std_logic_vector((DATA_WIDTH-1) downto 0);
	signal data_Rs2 	: std_logic_vector((DATA_WIDTH-1) downto 0);
	
	signal ALU_out		: std_logic_vector((DATA_WIDTH-1) downto 0);
	signal MDR			: std_logic_vector((DATA_WIDTH-1) downto 0);
	signal MemtoReg   : std_logic;
	
	signal PC_Wcond	: std_logic;
	signal PC_write 	: std_logic;
	signal PC_source	: std_logic;
	signal ALU_op		: std_logic_vector(3 downto 0);
	signal ALU_src1	: std_logic;
	signal ALU_src2	: std_logic_vector(1 downto 0);
	signal Jmp_enable	: std_logic; 
	signal IorD			: std_logic; 

	signal PC_enable	: std_logic;
	signal ZeroFlag	: std_logic;
	
	signal PC			: std_logic_vector((DATA_WIDTH-1) downto 0);
	signal ALU_in1		: std_logic_vector((DATA_WIDTH-1) downto 0);
	signal ALU_in2		: std_logic_vector((DATA_WIDTH-1) downto 0);
	signal Imm_ext		: std_logic_vector((DATA_WIDTH-1) downto 0);
	
	signal ALU_result	: std_logic_vector((DATA_WIDTH-1) downto 0);
	
	signal PC_input 	: std_logic_vector((DATA_WIDTH-1) downto 0);

	signal PC_Backup	: std_logic_vector((DATA_WIDTH-1) downto 0);
	signal PC_ALU		: std_logic_vector((DATA_WIDTH-1) downto 0);
	
	signal PC_ALU_sel	: std_logic;

begin
	
	IR: entity work.InstructionRegister(RTL) port map(instruction,IR_write,CLK,Reset,OpCode,Rd,Rs1,Rs2,Immediate);
	
	SignExt: entity work.SignExtent(dataflow) generic map(DATA_WIDTH) port map(Immediate,Imm_ext);
 
	MUX_Rs2: entity work.MUX_2x1(dataflow) generic map(Rs2'length) port map(Rs2,Rd,Rs2_select,GPReg_Rs2);
	
	Reg_File: entity work.GPReg_File(RTL) generic map(DATA_WIDTH,Rs2'length) port map(Rs1,GPReg_Rs2,Rd,GPRF_wr,data_in,CLK,Reset,data_Rs1,data_Rs2);

	MUX_MoR: entity work.MUX_2x1(dataflow) generic map(DATA_WIDTH) port map(ALU_out,MDR,MemtoReg,data_in);
	
	MDR_Reg: entity work.Reg(behavioral) generic map(DATA_WIDTH) port map(Instruction,CLK,Reset,'1',MDR);
	
	CU: entity work.ControlUnit(RTL) port map(OpCode,CLK,Reset,MemtoReg,GPRF_wr,IR_write,Mem_write,Rs2_select,PC_Wcond,Mem_read,PC_write,PC_source,
															ALU_op,ALU_src1,ALU_src2,Jmp_enable,IorD,Cu_state);
											
	PC_enable <= PC_write OR (Jmp_enable AND (PC_Wcond XNOR ZeroFlag));
	
	MUX1_ALU: entity work.MUX_2x1(dataflow) generic map(DATA_WIDTH) port map(data_Rs1,PC_ALU,ALU_src1,ALU_in1);
	
	MUX2_ALU: entity work.MUX_4x1(dataflow) generic map(DATA_WIDTH) port map(data_Rs2,x"0001",Imm_ext,x"0000",ALU_src2,ALU_in2); 
	
	ALU: entity work.ArithmeticLogicUnit(Behavioral) generic map(DATA_WIDTH) port map(ALU_in1,ALU_in2,ALU_op,ALU_result,ZeroFlag,flags);
	
	ALU_Reg: entity work.Reg(behavioral) generic map(DATA_WIDTH) port map(ALU_result,CLK,Reset,'1',ALU_out);
	
	MUX_PC: entity work.MUX_2x1(dataflow) generic map(DATA_WIDTH) port map(ALU_result,ALU_out,PC_source,PC_input);
	
	PC_Reg: entity work.Reg(behavioral) generic map(DATA_WIDTH) port map(PC_input,CLK,Reset,PC_enable,PC);
	
	MUX_IorD: entity work.MUX_2x1(dataflow) generic map(DATA_WIDTH) port map(PC,data_Rs1,IorD,i_address);
	
	i_data <= data_Rs2;

	PC_BACKUP_Reg: entity work.Reg(behavioral) generic map(DATA_WIDTH) port map(PC,CLK,Reset,PC_enable,PC_Backup);
	PC_ALU_sel <= (not ALU_src2(0)) AND ALU_src2(1);
	MUX_PC_ALU: entity work.MUX_2x1(dataflow) generic map(DATA_WIDTH) port map(PC,PC_Backup, PC_ALU_sel,PC_ALU);
	
	
end structural;