library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use IEEE.STD_LOGIC_UNSIGNED.all;
use work.CPU_library.all;

entity ArithmeticLogicUnit is

	generic(
				DATA_WIDTH 	: integer := 16				
	);
	
	port(
	
		--inputs
	
		Operand_A		:IN STD_LOGIC_VECTOR((DATA_WIDTH-1) DOWNTO 0);
		Operand_B		:IN STD_LOGIC_VECTOR((DATA_WIDTH-1) DOWNTO 0);
		Operation		:IN STD_LOGIC_VECTOR(3 downto 0);
		
		--outputs
		Output			:OUT STD_LOGIC_VECTOR((DATA_WIDTH-1) DOWNTO 0);
		ZeroFlag			:OUT STD_LOGIC; --CMP_s2_s1
		flags				:OUT STD_LOGIC_VECTOR(4 DOWNTO 0)	
		);
		
end ArithmeticLogicUnit;

architecture Behavioral of ArithmeticLogicUnit is

	signal flags_temp	: std_logic_vector(4 downto 0);

begin

process(Operation, Operand_A, Operand_B, flags_temp)
begin

		flags_temp <= "00000";


		case Operation is
			
			when ALU_ADD =>
			
				   Output <= Operand_A + Operand_B;
				
			when ALU_SUB =>
			
				if Operand_A > Operand_B then
					Output <= Operand_A - Operand_B;
				else
					Output <= Operand_B - Operand_A;
				end if;
			
			when ALU_AND =>
			
				Output <= Operand_A AND Operand_B;
				
			when ALU_OR =>
			
				Output <= Operand_A OR Operand_B;
			
			when ALU_NOT =>	
			
				Output <= NOT Operand_B;
			
			when ALU_XOR =>
			
				Output <= Operand_A XOR Operand_B;

			when ALU_CMP =>	
			
				if Operand_A = Operand_B then 
					flags_temp(0)  <= '1';
					Output(0) 		<= '1'; 
				else 
					flags_temp(0) 	<= '0';
					Output(0) 		<= '0'; 
				end if;
				
				if Operand_A = std_logic_vector(to_unsigned(0,DATA_WIDTH)) then 
					flags_temp(1) 	<= '1'; 
					Output(1) 		<= '1';
				else 
					flags_temp(1) 	<= '0'; 
					Output(1) 		<= '0';
				end if;
				
				if Operand_B = std_logic_vector(to_unsigned(0,DATA_WIDTH)) then 
					flags_temp(2) 	<= '1'; 
					Output(2) 		<= '1';
				else 
					flags_temp(2) 	<= '0'; 
					Output(2) 		<= '0';
				end if;
				if Operand_A > Operand_B then 
					flags_temp(3) 	<= '1';
					Output(3) 		<= '1';	
				else 
					flags_temp(3) 	<= '0'; 
					Output(3) 		<= '0';
				end if;
				
				if Operand_A < Operand_B then 
					flags_temp(4) 	<= '1'; 
					Output(4) 		<= '1';
				else 
					flags_temp(4) 	<= '0'; 
					Output(4) 		<= '0';
				end if;
				
				Output((DATA_WIDTH-1) downto 5) <= (others => '0');
				
			when ALU_SHL =>
			
				Output <= std_logic_vector(shift_left(unsigned(Operand_B),1));
			
			when ALU_SHR =>	
			
				Output <= std_logic_vector(shift_right(unsigned(Operand_B),1));
				
			when ALU_SEL_SRC2 =>
			
				Output <= Operand_B;
					
			when others => 
			
				Output <= (others => '0');
			
		end case;
		
end process;
		
		ZeroFlag <= flags_temp(2);
		flags <= flags_temp;


end Behavioral;