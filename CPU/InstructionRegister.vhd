library IEEE;
use IEEE.std_logic_1164.all;

entity InstructionRegister is
	
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

end InstructionRegister;


architecture RTL of InstructionRegister is
	--internal 16-bit register for storing the instruction
	signal inst_reg  : std_logic_vector(15 downto 0) := (others => '0');


begin

	Reg: process(CLK,Reset)
	begin
	
		if Reset = '1' then
			inst_reg <= (others => '0');
	
		elsif rising_edge(CLK) then
			if IR_write = '1' then
				
				inst_reg <= instruction; --load instruction to inst_reg when pos_edge
			
			end if;
	
		end if;

	end process;
	
	OpCode		<= inst_reg(15 downto 12); -- mostleft 4 bits are always opcode
	Rd 			<= inst_reg(11 downto 8);
	Rs1 			<= inst_reg(7 downto 4);
	Rs2 			<= inst_reg(3 downto 0);
	Immediate	<= inst_reg(7 downto 0);


end RTL; 



