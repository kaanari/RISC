library IEEE;
use IEEE.std_logic_1164.all;

entity InstructionRegister_tb is
end InstructionRegister_tb;

architecture testbench of InstructionRegister_tb is
	
	constant clk_period : time := 100 ps;

	signal instruction	:	std_logic_vector(15 downto 0) := (others => '0');
	signal IR_write	 	: 	std_logic := '0';
	signal CLK				:  std_logic;
	signal Reset			:  std_logic;
	signal OpCode			:  std_logic_vector(3 downto 0);
	signal Rd				:  std_logic_vector(3 downto 0);
	signal Rs1				:  std_logic_vector(3 downto 0);
	signal Rs2				:  std_logic_vector(3 downto 0);
	signal Immediate		:  std_logic_vector(7 downto 0);
	
	component InstructionRegister is
		
		port( 
				instruction	: in std_logic_vector(15 downto 0);
				IR_write		: in std_logic;
				CLK			: in std_logic;
				Reset			: in std_logic;
				OpCode		: out std_logic_vector(3 downto 0);
				Rd				: out std_logic_vector(3 downto 0);
				Rs1			: out std_logic_vector(3 downto 0);
				Rs2			: out std_logic_vector(3 downto 0);
				Immediate	: out std_logic_vector(7 downto 0)
		);

	end component;
	
	
begin
	
	UUT: InstructionRegister port map(instruction, IR_write, 
												 CLK, Reset, OpCode, 
												 Rd, Rs1, Rs2, Immediate);
	
	Clock: process
	begin
	
		CLK <= '0';
		wait for clk_period/2;
		CLK <= '1';
		wait for clk_period/2;
	
	end process;
	
	
	Stimulus: process
		variable case_num : integer range 0 to 100 := 1;
	begin

		
		Reset <= '1';
		wait for clk_period;
		Reset <= '0';
		--------------------
		instruction <= "1111011110111000";
		wait for clk_period;
		assert OpCode = "0000" and Rd = "0000" and Rs1 = "0000" and
				 Rs2 = "0000" and Immediate = "00000000" 
		report "Error found in case "& integer'image(case_num) & "!" 
		severity error;
		case_num := case_num + 1;
	   ------------------------------------------
		IR_write <= '1';
		wait for clk_period;
		assert OpCode = instruction(15 downto 12) and Rd = instruction(11 downto 8)
				 and Rs1 = instruction(7 downto 4) and Rs2 = instruction(3 downto 0)
				 and Immediate = instruction(7 downto 0)
		report "Error found in case "& integer'image(case_num) & "!" 
		severity error;
		case_num := case_num + 1;
		---------------------------------------------
		
		IR_write <= '0';
		instruction <= "0000000000000000";
		wait for clk_period;
		instruction <= "1111011110111000";
		wait for 2 ps;
		assert OpCode = instruction(15 downto 12) and Rd = instruction(11 downto 8)
				 and Rs1 = instruction(7 downto 4) and Rs2 = instruction(3 downto 0)
				 and Immediate = instruction(7 downto 0)
		report "Error found in case "& integer'image(case_num) & "!" 
		severity error;
		case_num := case_num + 1;
		wait for 2 ps;
		--------------------
		Reset <= '1';
		
		instruction <= "1111011110111000";
		wait for clk_period - 4 ps;
		assert OpCode = "0000" and Rd = "0000" and Rs1 = "0000" and
				 Rs2 = "0000" and Immediate = "00000000" 
		report "Error found in case "& integer'image(case_num) & "!" 
		severity error;
		case_num := case_num + 1;
		
		wait;
	end process;



end testbench;