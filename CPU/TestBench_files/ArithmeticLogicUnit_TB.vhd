LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.numeric_std.ALL;
use work.CPU_library.all;

ENTITY ArithmeticLogicUnit_TB IS
END ArithmeticLogicUnit_TB;

ARCHITECTURE TB OF ArithmeticLogicUnit_TB IS

		constant DATA_WIDTH	: integer := 16;
		
		signal flags_temp	: std_logic_vector(4 downto 0) := "00000";

component ArithmeticLogicUnit is

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
		
end component;
	
	SIGNAL Operand_A : STD_LOGIC_VECTOR((DATA_WIDTH-1) DOWNTO 0) := (others => '0');
	SIGNAL Operand_B : STD_LOGIC_VECTOR((DATA_WIDTH-1) DOWNTO 0) := (others => '0');
	SIGNAL Operation : STD_LOGIC_VECTOR(3 DOWNTO 0) := "0000";
	SIGNAL Output    : STD_LOGIC_VECTOR((DATA_WIDTH-1) DOWNTO 0);
	SIGNAL ZeroFlag  : STD_LOGIC;
	SIGNAL flags     : STD_LOGIC_VECTOR(4 DOWNTO 0);
	
	
	SIGNAL 	instruction : STRING (1 TO 7);
	CONSTANT op_time : TIME := 100 ps;
	SIGNAL 	exp_res : UNSIGNED((DATA_WIDTH-1) DOWNTO 0) := (others => '0'); -- Expected Result
	SIGNAL 	VALID : STD_LOGIC := '1';
	SIGNAL 	err_count : INTEGER := 0;
	
BEGIN

	UUT: ArithmeticLogicUnit PORT MAP(Operand_A, Operand_B, Operation, Output, ZeroFlag, flags);
	
	Stimulus: PROCESS
	
	BEGIN
		Operand_A <= "0101010101010101";
		Operand_B <= "0011001100110011";
		
		FOR i IN 0 TO 9 LOOP
			Operation <= std_logic_vector(to_unsigned(i, Operation'length));
			WAIT FOR 1 ps;
			IF exp_res /= unsigned(Output) THEN
				valid <= '0';
				err_count <= err_count + 1;
			ELSE
				valid <= '1';
			END IF;
			WAIT FOR op_time/2 - 1 ps;
			ASSERT (exp_res = unsigned(Output))
			REPORT "Unexpected Error WHEN " & instruction & "instruction"
				SEVERITY error;
				WAIT FOR op_time/2;
		END LOOP;

		Operand_A <= "0111011101110111";
		Operand_B <= "1011001100110011";
		
		FOR i IN 0 TO 9 LOOP
			Operation <= std_logic_vector(to_unsigned(i, Operation'length));
			WAIT FOR 1 ps;
			IF exp_res /= unsigned(Output) THEN
				valid <= '0';
				err_count <= err_count + 1;
			ELSE
				valid <= '1';
			END IF;
			WAIT FOR op_time/2 - 1 ps;
			ASSERT (exp_res = unsigned(Output))
			REPORT "Unexpected Error WHEN " & instruction & "instruction"
				SEVERITY error;
				WAIT FOR op_time/2;
		END LOOP;
		
		IF err_count = 0 THEN
			REPORT "No error occured." SEVERITY note;
		ELSE
			REPORT "Total " & INTEGER'image(err_count) & " error(s) occured."
				SEVERITY note;
		END IF;
		WAIT;
	END PROCESS;
	Check : PROCESS (Operation, Operand_A, Operand_B)
		VARIABLE mult : UNSIGNED(7 DOWNTO 0); -- Expected Result
	BEGIN
		CASE Operation IS
			WHEN ALU_ADD => exp_res <= unsigned(Operand_A) + unsigned(Operand_B);
			WHEN ALU_SUB => 
			
				if Operand_A > Operand_B then
					exp_res <= unsigned(Operand_A) - unsigned(Operand_B);
				else
					exp_res <= unsigned(Operand_B) - unsigned(Operand_A);
				end if;
				
			WHEN ALU_AND => exp_res <= unsigned(Operand_A) and unsigned(Operand_B);
			WHEN ALU_OR  => exp_res  <= unsigned(Operand_A) or unsigned(Operand_B);
			WHEN ALU_NOT => exp_res <= not unsigned(Operand_B);
			WHEN ALU_XOR => exp_res <= unsigned(Operand_A) xor unsigned(Operand_B);
			
			WHEN ALU_CMP => 
				if Operand_A = Operand_B then 
					flags_temp(0)  <= '1';
					exp_res(0) 		<= '1'; 
				else 
					flags_temp(0) 	<= '0';
					exp_res(0) 		<= '0'; 
				end if;
				
				if Operand_A = std_logic_vector(to_unsigned(0,DATA_WIDTH)) then 
					flags_temp(1) 	<= '1'; 
					exp_res(1) 		<= '1';
				else 
					flags_temp(1) 	<= '0'; 
					exp_res(1) 		<= '0';
				end if;
				
				if Operand_B = std_logic_vector(to_unsigned(0,DATA_WIDTH)) then 
					flags_temp(2) 	<= '1'; 
					exp_res(2) 		<= '1';
				else 
					flags_temp(2) 	<= '0'; 
					exp_res(2) 		<= '0';
				end if;
				if Operand_A > Operand_B then 
					flags_temp(3) 	<= '1';
					exp_res(3) 		<= '1';	
				else 
					flags_temp(3) 	<= '0'; 
					exp_res(3) 		<= '0';
				end if;
				
				if Operand_A < Operand_B then 
					flags_temp(4) 	<= '1'; 
					exp_res(4) 		<= '1';
				else 
					flags_temp(4) 	<= '0'; 
					exp_res(4) 		<= '0';
				end if;
				
				exp_res((DATA_WIDTH-1) downto 5) <= (others => '0');
				
			WHEN ALU_SHL => exp_res 		<= unsigned(Operand_B((DATA_WIDTH-2) downto 0) & '0');
			WHEN ALU_SHR => exp_res 		<= unsigned('0' & Operand_B((DATA_WIDTH-1) downto 1));
			WHEN ALU_SEL_SRC2 => exp_res 	<= unsigned(Operand_B);
			
			WHEN OTHERS => exp_res <= (others => '0');
			
		END CASE;
	END PROCESS;

	IDecoder : PROCESS (Operation)
	BEGIN
		CASE Operation IS
			WHEN ALU_ADD => 
				instruction <= "A+B    ";
			WHEN ALU_SUB => 
				instruction <= "A-B    ";
			WHEN ALU_AND => 
				instruction <= "A and B";
			WHEN ALU_OR => 
				instruction <= "A or B ";
			WHEN ALU_NOT => 
				instruction <= "not B  ";
			WHEN ALU_XOR => 
				instruction <= "A xor B";
			WHEN ALU_CMP => 
				instruction <= "cmp    ";
			WHEN ALU_SHL => 
				instruction <= "shl B  ";
			WHEN ALU_SHR => 
				instruction <= "shr B  ";
			WHEN ALU_SEL_SRC2 => 
				instruction <= "B      ";
			
			WHEN OTHERS => instruction <= "       ";
		END CASE;
	END PROCESS;
END TB;