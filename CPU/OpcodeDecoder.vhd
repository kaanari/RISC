library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use work.CPU_library.all;

entity OpcodeDecoder is

	port(
			OpCode : in std_logic_vector(3 downto 0);
			Operation : out std_logic_vector(15 downto 0)	
	);


end OpcodeDecoder;

architecture RTL of OpcodeDecoder is
begin
	
	process(OpCode)
	begin
	
		case OpCode is
		
			when ADD =>
				Operation <= (0 => '1', others => '0');
				
			when SUBx =>
				Operation <= (1 => '1', others => '0');
				
			when ANDx =>
				Operation <= (2 => '1', others => '0');
				
			when ORx =>
				Operation <= (3 => '1', others => '0');
				
			when NOTx =>
				Operation <= (4 => '1', others => '0');
				
			when XORx =>
				Operation <= (5 => '1', others => '0');
				
			when CMP =>
				Operation <= (6 => '1', others => '0');
				
			when SHL =>
				Operation <= (7 => '1', others => '0');
				
			when SHR =>
				Operation <= (8 => '1', others => '0');
				
			when LOAD =>
				Operation <= (9 => '1', others => '0');
				
			when STORE =>
				Operation <= (10 => '1', others => '0');
				
			when JUMP =>
				Operation <= (11 => '1', others => '0');
				
			when NOP =>
				Operation <= (12 => '1', others => '0');
				
			when JZ =>
				Operation <= (13 => '1', others => '0');
				
			when JNZ =>
				Operation <= (14 => '1', others => '0');
				
			when LOADI =>
				Operation <= (15 => '1', others => '0');
				
			when others =>
				Operation <= (others => '0');
				
		end case;

	end process;

end RTL;